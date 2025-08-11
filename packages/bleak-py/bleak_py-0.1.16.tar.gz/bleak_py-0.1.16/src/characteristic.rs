use btleplug::{
    api::{Characteristic as BtleCharacteristic, Peripheral as _, WriteType},
    platform::Peripheral,
    Result,
};
use std::pin::Pin;
use tokio_stream::{Stream, StreamExt};
use uuid::Uuid;

#[derive(Debug, Clone)]
pub struct Characteristic {
    pub(crate) peripheral: Peripheral,
    pub(crate) characteristic: BtleCharacteristic,
}

impl Characteristic {
    pub async fn read(&self) -> Result<Vec<u8>> {
        self.peripheral.read(&self.characteristic).await
    }

    pub async fn write_request(&self, data: &[u8]) -> Result<()> {
        self.write(data, WriteType::WithResponse).await
    }

    pub async fn write_command(&self, data: &[u8]) -> Result<()> {
        self.write(data, WriteType::WithoutResponse).await
    }

    #[inline]
    async fn write(&self, data: &[u8], write_type: WriteType) -> Result<()> {
        self.peripheral
            .write(&self.characteristic, data, write_type)
            .await
    }

    pub async fn subscribe(&self) -> Result<Pin<Box<dyn Stream<Item = Vec<u8>> + Send>>> {
        self.peripheral.subscribe(&self.characteristic).await?;

        let stream = self.peripheral.notifications().await?;
        let uuid = self.characteristic.uuid;

        Ok(Box::pin(stream.filter_map(move |n| {
            if n.uuid == uuid {
                Some(n.value)
            } else {
                None
            }
        })))
    }

    #[inline]
    pub async fn unsubscribe(&self) -> Result<()> {
        self.peripheral.unsubscribe(&self.characteristic).await
    }

    pub fn uuid(&self) -> Uuid {
        self.characteristic.uuid
    }
}
