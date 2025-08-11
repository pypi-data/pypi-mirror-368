/* Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
use crate::ConsumerOffsetClient;
use crate::client::binary_clients::BinaryClient;
use crate::utils::auth::fail_if_not_authenticated;
use crate::utils::mapper;
use iggy_common::delete_consumer_offset::DeleteConsumerOffset;
use iggy_common::get_consumer_offset::GetConsumerOffset;
use iggy_common::store_consumer_offset::StoreConsumerOffset;
use iggy_common::{Consumer, ConsumerOffsetInfo, Identifier, IggyError};

#[async_trait::async_trait]
impl<B: BinaryClient> ConsumerOffsetClient for B {
    async fn store_consumer_offset(
        &self,
        consumer: &Consumer,
        stream_id: &Identifier,
        topic_id: &Identifier,
        partition_id: Option<u32>,
        offset: u64,
    ) -> Result<(), IggyError> {
        fail_if_not_authenticated(self).await?;
        self.send_with_response(&StoreConsumerOffset {
            consumer: consumer.clone(),
            stream_id: stream_id.clone(),
            topic_id: topic_id.clone(),
            partition_id,
            offset,
        })
        .await?;
        Ok(())
    }

    async fn get_consumer_offset(
        &self,
        consumer: &Consumer,
        stream_id: &Identifier,
        topic_id: &Identifier,
        partition_id: Option<u32>,
    ) -> Result<Option<ConsumerOffsetInfo>, IggyError> {
        fail_if_not_authenticated(self).await?;
        let response = self
            .send_with_response(&GetConsumerOffset {
                consumer: consumer.clone(),
                stream_id: stream_id.clone(),
                topic_id: topic_id.clone(),
                partition_id,
            })
            .await?;
        if response.is_empty() {
            return Ok(None);
        }

        mapper::map_consumer_offset(response).map(Some)
    }

    async fn delete_consumer_offset(
        &self,
        consumer: &Consumer,
        stream_id: &Identifier,
        topic_id: &Identifier,
        partition_id: Option<u32>,
    ) -> Result<(), IggyError> {
        fail_if_not_authenticated(self).await?;
        self.send_with_response(&DeleteConsumerOffset {
            consumer: consumer.clone(),
            stream_id: stream_id.clone(),
            topic_id: topic_id.clone(),
            partition_id,
        })
        .await?;
        Ok(())
    }
}
