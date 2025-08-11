//! This example finds a BLE device with specified address.
//! cargo run --example filter_by_address XX:XX:XX:XX:XX:XX

use bleasy::{Filter, ScanConfig, Scanner};
use tokio_stream::StreamExt;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    rsutil::log::Log4rsConfig::default().initialize().unwrap();

    let address = std::env::args()
        .nth(1)
        .expect("Expected address in format XX:XX:XX:XX:XX:XX");

    log::info!("Scanning for device {}", address);

    let config = ScanConfig::default()
        .with_filters(&vec![Filter::Address(address.clone())])
        .filter_by_address(move |addr| addr.eq(&address))
        .stop_after_first_match();

    let mut scanner = Scanner::new();
    scanner.start(config).await?;

    let device = scanner.device_stream()?.next().await;

    println!("{:?}", device.unwrap().local_name().await);

    Ok(())
}
