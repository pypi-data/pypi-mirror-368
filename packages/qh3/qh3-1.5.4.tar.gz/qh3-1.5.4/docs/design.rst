Design
======

Sans-IO APIs
............

Both the QUIC and the HTTP/3 APIs follow the `sans I/O`_ pattern, leaving
actual I/O operations to the API user. This approach has a number of
advantages including making the code testable and allowing integration with
different concurrency models.

TLS and encryption
..................

TLS 1.3
+++++++

``qh3`` features a minimal TLS 1.3 implementation built upon the
`aws-lc-rs`_ library. This is because QUIC requires some APIs which are
currently unavailable in mainstream TLS implementations such as OpenSSL:

- the ability to extract traffic secrets

- the ability to operate directly on TLS messages, without using the TLS
  record layer

Header protection and payload encryption
++++++++++++++++++++++++++++++++++++++++

QUIC makes extensive use of cryptographic operations to protect QUIC packet
headers and encrypt packet payloads. These operations occur for every single
packet and are a determining factor for performance. For this reason, they
are implemented in Rust.

.. _sans I/O: https://sans-io.readthedocs.io/
.. _aws-lc-rs: https://github.com/aws/aws-lc-rs
