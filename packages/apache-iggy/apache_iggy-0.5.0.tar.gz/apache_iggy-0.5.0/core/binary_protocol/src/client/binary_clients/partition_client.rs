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

use async_trait::async_trait;
use iggy_common::{Identifier, IggyError};

/// This trait defines the methods to interact with the partition module.
#[async_trait]
pub trait PartitionClient {
    /// Create new N partitions for a topic by unique ID or name.
    ///
    /// For example, given a topic with 3 partitions, if you create 2 partitions, the topic will have 5 partitions (from 1 to 5).
    ///
    /// Authentication is required, and the permission to manage the partitions.
    async fn create_partitions(
        &self,
        stream_id: &Identifier,
        topic_id: &Identifier,
        partitions_count: u32,
    ) -> Result<(), IggyError>;
    /// Delete last N partitions for a topic by unique ID or name.
    ///
    /// For example, given a topic with 5 partitions, if you delete 2 partitions, the topic will have 3 partitions left (from 1 to 3).
    ///
    /// Authentication is required, and the permission to manage the partitions.
    async fn delete_partitions(
        &self,
        stream_id: &Identifier,
        topic_id: &Identifier,
        partitions_count: u32,
    ) -> Result<(), IggyError>;
}
