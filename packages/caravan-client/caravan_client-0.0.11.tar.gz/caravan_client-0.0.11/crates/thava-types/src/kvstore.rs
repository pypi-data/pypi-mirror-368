use redis::Commands;

/// Contains connections to both Redis databases Caravan utilizes
/// First DB: (RId, SerializedTensor)
/// Second DB: (WorkerID, Vec<RId>)
pub struct RedisConnections {
    pub rid_tensor_con: redis::Connection,
    pub worker_rid_con: redis::Connection,
}

/// Assemble URL for Redis connection
/// TODO: Get Redis info through environment variables
fn get_rid_tensor_connection_url() -> String {
    //    let redis_username = std::env::var("REDIS_USERNAME").unwrap_or("".to_string());
    //    let redis_password = std::env::var("REDIS_PASSWORD").unwrap_or("".to_string());

    let user = "default".to_string();
    let pass = "qjhwN3y3omYblSUt7MisKMQDctqKkTGt".to_string();

    format!(
        "redis://{}:{}@redis-15880.c228.us-central1-1.gce.redns.redis-cloud.com:15880/db",
        user, pass
    )
}

fn get_wid_rid_connection_url() -> String {
    let user = "default".to_string();
    let pass = "Q4jYXW3tzbZRKn5la3kqHDEbY4ezMZIB".to_string();

    format!(
        "redis://{}:{}@redis-19172.c331.us-west1-1.gce.redns.redis-cloud.com:19172/db",
        user, pass
    )
}

/// Get a client to the thava Redis server
pub fn get_rid_tensor_client() -> redis::Client {
    redis::Client::open(get_rid_tensor_connection_url()).unwrap()
}

pub fn get_wid_rid_client() -> redis::Client {
    redis::Client::open(get_wid_rid_connection_url()).unwrap()
}

/// Get a connection to the thava Redis server
pub fn get_redis_connection() -> redis::RedisResult<RedisConnections> {
    let rid_tensor_client = get_rid_tensor_client();
    let wid_rid_client = get_wid_rid_client();

    let rid_tensor_con = rid_tensor_client.get_connection()?;
    let wid_rid_con = wid_rid_client.get_connection()?;

    let con = RedisConnections {
        rid_tensor_con,
        worker_rid_con: wid_rid_con,
    };

    Ok(con)
}

/// Get a value from the Redis server
/// In Caravan the key-value pair is a tensor (RId, Value)
pub fn get_value(key: &str, con: &mut redis::Connection) -> redis::RedisResult<String> {
    let value: String = con.get(key)?;

    Ok(value)
}

/// Set a key-value pair in the Redis server
/// In Caravan the key-value pair is a tensor (RId, Value)
pub fn set_value(key: &str, value: &str, con: &mut RedisConnections) -> redis::RedisResult<()> {
    let _: () = con.rid_tensor_con.set(key, value)?;
    Ok(())
}

/// Get multiple values from the Redis server
/// In Caravan the key-value pair is a tensor (RId, Value)
pub fn get_multiple_values(
    keys: Vec<&str>,
    con: &mut redis::Connection,
) -> redis::RedisResult<Vec<String>> {
    let values: Vec<String> = con.mget(keys)?;

    Ok(values)
}

/// Set multiple key-value pairs in the Redis server
/// In Caravan the key-value pair is a tensor (RId, Value)
pub fn set_multiple_values(
    kv_pairs: Vec<(&str, &str)>,
    con: &mut redis::Connection,
) -> redis::RedisResult<()> {
    let _: () = con.mset(&kv_pairs)?;

    Ok(())
}
