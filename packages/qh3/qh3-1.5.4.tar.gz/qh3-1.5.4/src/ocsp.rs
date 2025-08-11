// OCSP Response Parser and Request Builder
// This module is created for Niquests
// qh3 has no use for it and we won't implement it for this package
use pyo3::pymethods;
use pyo3::types::PyBytesMethods;
use pyo3::types::{PyBytes, PyType};
use pyo3::{pyclass, Bound};
use pyo3::{PyResult, Python};

use der::{Decode, Encode};
use pyo3::exceptions::PyValueError;
use x509_cert::Certificate;
use x509_ocsp::builder::OcspRequestBuilder;
use x509_ocsp::{
    BasicOcspResponse, CertStatus as InternalCertStatus, OcspRequest as InternalOcspRequest,
    OcspResponse, OcspResponseStatus as InternalOcspResponseStatus, Request, SingleResponse,
};

use bincode::{deserialize, serialize};
use serde::{Deserialize, Serialize};
use sha1::Sha1;

use crate::chain::is_parent;
use crate::verify::{context_for_verify, verify_signature};
use x509_parser::certificate::X509Certificate;
use x509_parser::nom::AsBytes;
use x509_parser::prelude::AlgorithmIdentifier;
use x509_parser::prelude::FromDer;

#[pyclass(module = "qh3._hazmat", eq, eq_int)]
#[derive(Clone, Copy, Serialize, Deserialize, PartialEq, Debug)]
#[allow(non_camel_case_types)]
pub enum ReasonFlags {
    unspecified = 0,
    key_compromise = 1,
    ca_compromise = 2,
    affiliation_changed = 3,
    superseded = 4,
    cessation_of_operation = 5,
    certificate_hold = 6,
    privilege_withdrawn = 9,
    aa_compromise = 10,
    remove_from_crl = 8,
}

#[pyclass(module = "qh3._hazmat", eq, eq_int)]
#[derive(Clone, Copy, Serialize, Deserialize, PartialEq)]
#[allow(non_camel_case_types)]
pub enum OCSPResponseStatus {
    SUCCESSFUL = 0,
    MALFORMED_REQUEST = 1,
    INTERNAL_ERROR = 2,
    TRY_LATER = 3,
    SIG_REQUIRED = 5,
    UNAUTHORIZED = 6,
}

#[pyclass(module = "qh3._hazmat", eq, eq_int)]
#[derive(Clone, Copy, Serialize, Deserialize, PartialEq)]
#[allow(non_camel_case_types)]
pub enum OCSPCertStatus {
    GOOD = 0,
    REVOKED = 1,
    UNKNOWN = 2,
}

#[pyclass(module = "qh3._hazmat")]
#[derive(Clone, Serialize, Deserialize)]
#[allow(non_camel_case_types)]
pub struct OCSPResponse {
    next_update: u64,
    response_status: OCSPResponseStatus,
    certificate_status: OCSPCertStatus,
    revocation_reason: Option<ReasonFlags>,
    raw: Vec<u8>,
}

#[pymethods]
impl OCSPResponse {
    #[new]
    pub fn py_new(raw_response: Bound<'_, PyBytes>) -> PyResult<Self> {
        let ocsp_res: OcspResponse = match OcspResponse::from_der(raw_response.as_bytes()) {
            Ok(ocsp_res) => ocsp_res,
            Err(_) => return Err(PyValueError::new_err("OCSP DER given is invalid")),
        };

        if ocsp_res.response_bytes.is_none() {
            return Err(PyValueError::new_err("OCSP Server did not provide answers"));
        }

        let inner_resp: BasicOcspResponse =
            BasicOcspResponse::from_der(ocsp_res.response_bytes.unwrap().response.as_bytes())
                .unwrap();

        if inner_resp.tbs_response_data.responses.is_empty() {
            return Err(PyValueError::new_err("OCSP Server did not provide answers"));
        }

        let first_resp_for_cert: &SingleResponse = &inner_resp.tbs_response_data.responses[0];

        Ok(OCSPResponse {
            next_update: first_resp_for_cert
                .next_update
                .unwrap()
                .0
                .to_unix_duration()
                .as_secs(),
            response_status: match ocsp_res.response_status {
                InternalOcspResponseStatus::Successful => OCSPResponseStatus::SUCCESSFUL,
                InternalOcspResponseStatus::MalformedRequest => {
                    OCSPResponseStatus::MALFORMED_REQUEST
                }
                InternalOcspResponseStatus::InternalError => OCSPResponseStatus::INTERNAL_ERROR,
                InternalOcspResponseStatus::TryLater => OCSPResponseStatus::TRY_LATER,
                InternalOcspResponseStatus::SigRequired => OCSPResponseStatus::SIG_REQUIRED,
                InternalOcspResponseStatus::Unauthorized => OCSPResponseStatus::UNAUTHORIZED,
            },
            certificate_status: match first_resp_for_cert.cert_status {
                InternalCertStatus::Good(..) => OCSPCertStatus::GOOD,
                InternalCertStatus::Revoked(_) => OCSPCertStatus::REVOKED,
                InternalCertStatus::Unknown(_) => OCSPCertStatus::UNKNOWN,
            },
            revocation_reason: match first_resp_for_cert.cert_status {
                InternalCertStatus::Revoked(info) => match info.revocation_reason {
                    Some(reason) => match reason as u8 {
                        0 => Some(ReasonFlags::unspecified),
                        1 => Some(ReasonFlags::key_compromise),
                        2 => Some(ReasonFlags::ca_compromise),
                        3 => Some(ReasonFlags::affiliation_changed),
                        4 => Some(ReasonFlags::superseded),
                        5 => Some(ReasonFlags::cessation_of_operation),
                        6 => Some(ReasonFlags::certificate_hold),
                        8 => Some(ReasonFlags::remove_from_crl),
                        9 => Some(ReasonFlags::privilege_withdrawn),
                        10 => Some(ReasonFlags::aa_compromise),
                        _ => None,
                    },
                    _ => None,
                },
                InternalCertStatus::Good(_) | InternalCertStatus::Unknown(_) => None,
            },
            raw: raw_response.as_bytes().to_vec(),
        })
    }

    #[getter]
    pub fn next_update(&self) -> u64 {
        self.next_update
    }

    #[getter]
    pub fn response_status(&self) -> OCSPResponseStatus {
        self.response_status
    }

    #[getter]
    pub fn certificate_status(&self) -> OCSPCertStatus {
        self.certificate_status
    }

    #[getter]
    pub fn revocation_reason(&self) -> Option<ReasonFlags> {
        self.revocation_reason
    }

    pub fn authenticate_for(&self, issuer_der: Bound<'_, PyBytes>) -> PyResult<bool> {
        let issuer = X509Certificate::from_der(issuer_der.as_bytes()).unwrap().1;

        let ocsp_res: OcspResponse = match OcspResponse::from_der(self.raw.as_ref()) {
            Ok(ocsp_res) => ocsp_res,
            Err(_) => return Err(PyValueError::new_err("OCSP DER given is invalid")),
        };

        if ocsp_res.response_bytes.is_none() {
            return Err(PyValueError::new_err("OCSP Server did not provide answers"));
        }

        let raw_ocsp_response = ocsp_res.response_bytes.unwrap();

        let inner_resp: BasicOcspResponse =
            BasicOcspResponse::from_der(raw_ocsp_response.response.as_bytes()).unwrap();

        if inner_resp.tbs_response_data.responses.is_empty() {
            return Err(PyValueError::new_err("OCSP Server did not provide answers"));
        }

        // applying some trick to get that signature algorithm matching
        // the x509_parser inner struct.
        let der_bytes = inner_resp.signature_algorithm.to_der().unwrap();

        // Convert to AlgorithmIdentifier
        let res = AlgorithmIdentifier::from_der(der_bytes.as_slice());

        if res.is_err() {
            return Err(PyValueError::new_err(
                "Unable to extract ocsp response signature algorithm identifier",
            ));
        }

        let algorithm = res.unwrap().1;

        // this branch handle the case where the issuer CA
        // does not have EKU OCSP signing, they probably issued
        // one or many intermediate to be capable of signing OCSP
        // responses.
        if inner_resp.certs.is_some() {
            let der_blobs: Vec<Vec<u8>> = inner_resp
                .certs
                .as_ref()
                .unwrap()
                .iter()
                .map(|crt| crt.to_der().expect("DER encoding failed"))
                .collect();

            let mut extra_chain: Vec<X509Certificate<'_>> = der_blobs
                .iter()
                .map(|der| {
                    let (_, cert) = X509Certificate::from_der(der).expect("parse failed");
                    cert
                })
                .collect();

            extra_chain.push(issuer);

            for child_parent in extra_chain.windows(2) {
                if is_parent(&child_parent[0], &child_parent[1]).is_err() {
                    return Ok(false);
                }
            }

            let immediate_issuer = &extra_chain[0];

            let ctx_verify = match context_for_verify(&algorithm, immediate_issuer) {
                Some(ctx) => ctx,
                None => {
                    return Err(PyValueError::new_err(
                        "Unable to verify ocsp response signature (algorithm unsupported)",
                    ))
                }
            };

            Ok(verify_signature(
                ctx_verify.1.as_bytes(),
                ctx_verify.0,
                inner_resp.tbs_response_data.to_der().unwrap().as_bytes(),
                inner_resp.signature.as_bytes().unwrap(),
            )
            .is_ok())
        } else {
            // simplest case, the issuer can directly sign those! (most common)
            let ctx_verify = match context_for_verify(&algorithm, &issuer) {
                Some(ctx) => ctx,
                None => {
                    return Err(PyValueError::new_err(
                        "Unable to verify ocsp response signature (algorithm unsupported)",
                    ))
                }
            };

            Ok(verify_signature(
                ctx_verify.1.as_bytes(),
                ctx_verify.0,
                inner_resp.tbs_response_data.to_der().unwrap().as_bytes(),
                inner_resp.signature.as_bytes().unwrap(),
            )
            .is_ok())
        }
    }

    pub fn serialize<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyBytes>> {
        Ok(PyBytes::new(py, &serialize(&self).unwrap()))
    }

    #[classmethod]
    pub fn deserialize(_cls: Bound<'_, PyType>, encoded: Bound<'_, PyBytes>) -> PyResult<Self> {
        Ok(deserialize(encoded.as_bytes()).unwrap())
    }
}

#[pyclass(module = "qh3._hazmat")]
pub struct OCSPRequest {
    inner_request: Vec<u8>,
}

#[pymethods]
impl OCSPRequest {
    #[new]
    pub fn py_new(
        peer_certificate: Bound<'_, PyBytes>,
        issuer_certificate: Bound<'_, PyBytes>,
    ) -> PyResult<Self> {
        let issuer = Certificate::from_der(issuer_certificate.as_bytes()).unwrap();
        let cert = Certificate::from_der(peer_certificate.as_bytes()).unwrap();

        let req: InternalOcspRequest = OcspRequestBuilder::default()
            .with_request(Request::from_cert::<Sha1>(&issuer, &cert).unwrap())
            .build();

        match req.to_der() {
            Ok(raw_der) => Ok(OCSPRequest {
                inner_request: raw_der,
            }),
            Err(_) => Err(PyValueError::new_err("unable to generate the request")),
        }
    }

    pub fn public_bytes<'a>(&self, py: Python<'a>) -> Bound<'a, PyBytes> {
        PyBytes::new(py, &self.inner_request)
    }
}
