// ---------------------------------------------------------------------
// twamp-sender collector
// ---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
// ---------------------------------------------------------------------

mod config;
pub use config::TWAMPSenderConfig;

cfg_if::cfg_if! {
    if #[cfg(feature = "twamp-sender")] {
        mod collector;
        pub use collector::TWAMPSenderCollector;
    } else {
        use super::StubCollector;
        pub type TWAMPSenderCollector = StubCollector<TWAMPSenderConfig>;
    }
}