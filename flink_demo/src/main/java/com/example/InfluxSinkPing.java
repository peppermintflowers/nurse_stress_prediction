package com.example;

import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.functions.sink.RichSinkFunction;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

public class InfluxSinkPing extends RichSinkFunction<IOTPing> {
    private String influxUrl;

    @Override
    public void open(Configuration parameters) {
        influxUrl = "http://influxdb:8086/write?db=flink_sink";
    }

    @Override
    public void invoke(IOTPing ping, Context ctx) throws Exception {
        String line = String.format(
                "flink_events,id=%d feature=%d,multiplied=%d",
                ping.id,
                ping.feature,
                ping.multiplied
        );

        URL url = new URL(influxUrl);
        HttpURLConnection con = (HttpURLConnection) url.openConnection();
        con.setRequestMethod("POST");
        con.setDoOutput(true);

        try (OutputStream os = con.getOutputStream()) {
            os.write(line.getBytes());
        }

        int code = con.getResponseCode();
        if (code >= 400) {
            System.err.println("InfluxDB write failed: HTTP " + code);
        }

        con.disconnect();
    }
}
