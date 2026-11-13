# Checkout API POC

Small public API boundary used by the Spec 045 runtime-evidence cohort.

This repository owns the customer-facing checkout authorization response. It
calls the session-validation service through `SessionGateway` and translates
its result into a stable HTTP payload. Session-provider selection and remote
authentication belong to the separate runtime-session service.

