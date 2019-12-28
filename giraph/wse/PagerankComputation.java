package wse;

import org.apache.giraph.graph.BasicComputation;
import org.apache.giraph.graph.Vertex;
import org.apache.hadoop.io.Writable;
import org.apache.hadoop.io.WritableComparable;

import org.apache.giraph.conf.LongConfOption;
import org.apache.giraph.edge.Edge;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.log4j.Logger;

import java.io.IOException;
import java.lang.Math;

public class PagerankComputation extends BasicComputation<
        LongWritable, Text, LongWritable, Text> {

    public static final int MAX_SUPERSTEPS = 200;
    public static final double M = 0.15;

    @Override
    public void compute(Vertex<LongWritable, Text, LongWritable> vertex,
                        Iterable<Text> messages) throws IOException {
        if (getSuperstep() == 0) {
            double x = M/getTotalNumVertices();
            double z = M/getTotalNumVertices();
            vertex.setValue(new Text(String.format("%f,%f", x, z)));
        } else if (getSuperstep() < MAX_SUPERSTEPS) {
            boolean isUpdating = Math.random() < 0.5;

            double x;
            double z;
            String[] values = vertex.getValue().toString().split(",");
            x = Double.parseDouble(values[0]);
            z = Double.parseDouble(values[1]);

            if (isUpdating) {
                double n;
                n = vertex.getNumEdges();

                Text message_aux = new Text(String.format("%f,%f", n, z));
                for (Edge<LongWritable, LongWritable> edge : vertex.getEdges()) {
                    sendMessage(edge.getTargetVertexId(), message_aux);
                }
            }

            z = isUpdating ? 0 : z;
            double nj;
            double zj;
            for (Text message : messages) {
                values = message.toString().split(",");
                nj = Double.parseDouble(values[0]);
                zj = Double.parseDouble(values[1]);

                x += ((1 - M)/nj)*zj;
                z += ((1 - M)/nj)*zj;
            }
            vertex.setValue(new Text(String.format("%f,%f", x, z)));
        } else {
            vertex.voteToHalt();
        }
    }
}
