package com.nurse.stress.prediction.processing;

public interface Constants {
    String BROKER_URL="kafka:9092";
    String TOPIC_NAME="stress-topic";
    String GROUP_ID = "flink-consumer";
    String INFLUX_URL= "http://influxdb:8086";
    String JOB_SINK_INFLUX_DB= "flink_sink";
}
