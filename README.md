# Distributed PageRank

This repository implements distributed PageRank computation following the works of [Suzuki and Ishii](https://arxiv.org/abs/1907.09979).

Three implementations are available: in Python, in Go, and in Apache Giraph.

In order to execute the algorithm in large graphs, the Apache Giraph implementation is recommended using a Hadoop cluster. For illustration purposes, we provide instructions on how to execute the Apache Giraph implementation in a standalone Hadoop cluster using [this Docker container](https://github.com/uwsampa/giraph-docker).

4 graphs are available in `graphs`: `graph.txt` (8 edges), `soc-karate.mtx` (78 edges), `soc-wiki-Vote.mtx` (2,914 edges), and `web-Google.txt` (5,105,038 edges). By default, all implementations are executed on `graph.txt`.

As reference, `python/pagerank.py` computes PageRank using the [NetworkX](https://networkx.github.io/) library and can be used for correctness comparison.

## Directories

- `giraph`: Apache Giraph implementation
- `go`: Go implementation
- `python`: Python implementations
- `graphs`: Directed graphs stored as edges

## Python

### Requirements
- Python 3
- NetworkX

### Running

```bash
$ python python/algorithm3.py
{'0': 0.2606881439958283, '1': 0.14079246119822697, '4': 0.27139791783809986, '2': 0.16060545663987302, '3': 0.1665145745051986}
```

## Go

### Requirements
- Go 1.13.5
-

### Running
```bash
$ go run go/algorithm.go
0 (x: 0.260689 z: 0.000000)
1 (x: 0.140793 z: 0.000000)
4 (x: 0.271398 z: 0.000000)
2 (x: 0.160606 z: 0.000000)
3 (x: 0.166515 z: 0.000000)
```

## Apache Giraph

### Requirements
- Hadoop 2.4.1
- Giraph 1.1.0

### Installing

**Recommended:** Use this [Docker](https://github.com/uwsampa/giraph-docker) image

#### Docker

##### Installing Docker image
```bash
$ cd <project-root>
$ docker pull uwsampa/giraph-docker
$ docker run --volume $(pwd):/myhome --rm --interactive --tty uwsampa/giraph-docker /etc/giraph-bootstrap.sh -bash
```

##### Running

Prepare input:

```bash
$ $HADOOP_HOME/bin/hdfs dfs -put graphs/graph.txt /user/root/input/graph.txt
```

Execute job:

```bash
$ javac -cp /usr/local/giraph/giraph-examples/target/giraph-examples-1.1.0-SNAPSHOT-for-hadoop-2.4.1-jar-with-dependencies.jar:$($HADOOP_HOME/bin/hadoop classpath) wse/*.java
$ cp /usr/local/giraph/giraph-examples/target/giraph-examples-1.1.0-SNAPSHOT-for-hadoop-2.4.1-jar-with-dependencies.jar ./myjar.jar
$ jar uf myjar.jar wse
$ $HADOOP_HOME/bin/hadoop jar myjar.jar org.apache.giraph.GiraphRunner wse.PagerankComputation --yarnjars myjar.jar --workers 1 -eif wse.LongLongDefaultEdgeValueTextEdgeInputFormat -eip /user/root/input/graph.txt -vertexOutputFormat org.apache.giraph.io.formats.IdWithValueTextOutputFormat --outputPath /user/root/output
$ $HADOOP_HOME/bin/hdfs dfs -cat /user/root/dummy-output/part-m-00001
```

#### NYU HPC

##### Installing Apache Giraph

```bash
$ module load maven
$ git clone https://github.com/apache/giraph.git
$ cd giraph
$ mvn -Phadoop_2 -Dhadoop.version=2.6.0 -DskipTests package
```

##### Running

Prepare input:

```bash
$ $HADOOP_HOME/bin/hdfs dfs -put graphs/graph.txt /user/root/input/graph.txt
0   0.260702,0.000003
2   0.160610,0.000001
1   0.140799,0.000000
3   0.166521,0.000000
4   0.271411,0.000001
```

Execute job:

```bash
$ hdfs dfs -rm -r -f giraph/output
$ javac -cp $GIRAPH_HOME/giraph-core/target/giraph-1.3.0-SNAPSHOT-for-hadoop-2.6.0-jar-with-dependencies.jar:$(hadoop classpath) wse/*.java
$ cp $GIRAPH_HOME/giraph-core/target/giraph-1.3.0-SNAPSHOT-for-hadoop-2.6.0-jar-with-dependencies.jar ./myjar.jar
$ jar uf myjar.jar wse
$ hadoop jar myjar.jar org.apache.giraph.GiraphRunner wse.PagerankComputation --yarnjars myjar.jar -eif wse.LongLongDefaultEdgeValueTextEdgeInputFormat -eip /user/mvp307/giraph/input/graph.txt -vertexOutputFormat org.apache.giraph.io.formats.IdWithValueTextOutputFormat --outputPath /user/mvp307/giraph/output --workers 3
$ hdfs dfs -cat giraph/output/part-m-00001

```