use bleasy::{ScanConfig, Scanner};
use std::sync::{
    atomic::{AtomicU32, Ordering},
    Arc,
};
use tokio::time::{sleep, Duration};
use tokio_stream::StreamExt;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    rsutil::log::Log4rsConfig::default().initialize().unwrap();

    // Create a new BLE device scanner
    let mut scanner = Scanner::new();

    // Start the scanner with default configuration
    scanner.start(ScanConfig::default()).await?;

    // Create a stream that is provided with discovered devices
    let mut device_stream = scanner.device_stream()?;

    // Create a thread-safe counter
    let count = Arc::new(AtomicU32::new(0));

    // List devices in a separate thread as they are discovered
    let join_handle = {
        let count = count.clone();
        tokio::spawn(async move {
            while let Some(device) = device_stream.next().await {
                println!("Found device with name {:?}", device.local_name().await);
                count.fetch_add(1, Ordering::SeqCst);
            }
        })
    };

    // Wait until at least two devices are found
    while count.load(Ordering::SeqCst) < 2 {
        sleep(Duration::from_millis(100)).await;
    }

    // Stop the scanner after 2 devices are found
    scanner.stop().await?;

    join_handle.await?;

    Ok(())
}
