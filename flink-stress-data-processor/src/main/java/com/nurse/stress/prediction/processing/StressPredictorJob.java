package com.nurse.stress.prediction.processing;

import com.nurse.stress.prediction.SensorRecord;
import com.nurse.stress.prediction.model.IOTPing;
import com.nurse.stress.prediction.model.NurseMetrics;
import com.nurse.stress.prediction.sink.InfluxSinkPing;
import com.nurse.stress.prediction.source.KafkaSourceFactory;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows;

import java.time.Duration;


public class StressPredictorJob {

    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(2);

        KafkaSource<SensorRecord> source = KafkaSourceFactory.create(Constants.BROKER_URL, Constants.TOPIC_NAME);

        DataStream<SensorRecord> records = env.fromSource(source,WatermarkStrategyFactory.create(),"Kafka Source");

        DataStream<IOTPing> predictedStress = records.keyBy(r->r.getId())
                .window(TumblingEventTimeWindows.of(Duration.ofMinutes(1)))
                .aggregate(new AverageAggregator(),new WindowResultFunction())
                .name("Stress Prediction 1 minute batch")
                .map(n -> new IOTPing(
                        n.getId(),
                        n.getEDA(),
                        n.getHR(),
                        n.getTEMP(),
                        n.getDatetime(),
                        0
                ));

        predictedStress.addSink(new InfluxSinkPing());
        env.execute("Flink Streaming Metrics Example");
    }
}

