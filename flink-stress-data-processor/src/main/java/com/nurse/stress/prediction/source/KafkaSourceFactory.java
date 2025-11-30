package com.nurse.stress.prediction.source;

import com.nurse.stress.prediction.SensorRecord;
import com.nurse.stress.prediction.processing.Constants;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.formats.avro.AvroDeserializationSchema;

public class KafkaSourceFactory {


    public static KafkaSource<SensorRecord> create(String brokers, String topics){
        return KafkaSource.<SensorRecord>builder()
                .setBootstrapServers(brokers)
                .setTopics(topics)
                .setGroupId(Constants.GROUP_ID)
                .setValueOnlyDeserializer(AvroDeserializationSchema.forSpecific(SensorRecord.class))
                .build();
    }
}
