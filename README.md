# Hadoop MapReduce — Amazon Electronics Review Rating Analysis

A MapReduce pipeline built on Apache Hadoop 3 (via Docker) that processes **3.8 million Amazon Electronics reviews** to analyze rating distributions using Python `mrjob` and HDFS.

---

## 📊 Results

| Rating | Count     |
|--------|-----------|
| ⭐ 1   | 397,593   |
| ⭐⭐ 2  | 196,151   |
| ⭐⭐⭐ 3 | 278,893   |
| ⭐⭐⭐⭐ 4 | 669,593  |
| ⭐⭐⭐⭐⭐ 5 | 2,260,251 |

**Total reviews processed: ~3.8 million** (processed from a 2.4GB JSON file on a single-node cluster)

### Key Findings

1. **J-shaped distribution** — 57% of reviews are 5-star. Electronics buyers tend to polarize: either thrilled or disappointed, with few neutral reviews.
2. **Unhappy reviewers are louder** — 1-star reviews (397,593) outnumber 2-star (196,151) and 3-star (278,893) combined, showing that dissatisfied customers are roughly 2× more likely to leave a review than neutral ones.
3. **MapReduce scales efficiently** — A single mapper + reducer processed 3.8M records reliably, producing exactly 5 output records (one per rating value), confirming correct logic.

---

## 🗂 Repository Structure

```
hadoop-mapreduce-amazon-reviews/
├── rating_count.py       # MRJob MapReduce script for rating distribution
├── docker-compose.yml    # Single-node Hadoop cluster setup (namenode + datanode)
└── README.md
```

---

## 🛠 Tech Stack

- **Apache Hadoop 3.3.6** — deployed via `apache/hadoop:3` Docker image
- **HDFS** — distributed file system for input/output data
- **Hadoop Streaming** — runs the Python script as a MapReduce job
- **Apache Hive 3.1.3** — SQL-layer for schema exploration
- **Python `mrjob`** — MapReduce job definition
- **Docker + Docker Compose** — single-node cluster orchestration
- **Dataset** — [Amazon Electronics Reviews v2](https://cseweb.ucsd.edu/~jmcauley/datasets/amazon_v2/) (JSON, ~11.5GB full / 2.4GB subset used)

---

## 🚀 Getting Started

### Prerequisites

- Docker Desktop (v29+) with WSL 2 backend (Windows) or native Linux/macOS
- At least 4GB RAM allocated to Docker
- Python 3 + `mrjob` installed locally (for local testing only)

### 1. Start the Hadoop Cluster

```bash
docker-compose up -d
```

This starts a `namenode` and `datanode` container using the official `apache/hadoop:3` image.

### 2. Verify Hadoop is Running

```bash
docker exec -it namenode hadoop version
docker exec -it namenode hdfs dfsadmin -report
```

### 3. Upload the Dataset to HDFS

Download the Amazon Electronics dataset and copy it into the namenode:

```bash
docker cp Electronics.json namenode:/tmp/Electronics.json
docker exec -it namenode hdfs dfs -mkdir -p /data
docker exec -it namenode hdfs dfs -put /tmp/Electronics.json /data/Electronics.json
```

Verify:
```bash
docker exec -it namenode hdfs dfs -ls /data
```

### 4. Copy the MapReduce Script

```bash
docker cp rating_count.py namenode:/tmp/rating_count.py
```

### 5. Run the MapReduce Job

```bash
docker exec -it namenode hadoop jar \
  /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
  -files /tmp/rating_count.py \
  -mapper "python3 rating_count.py --step-num=0 --mapper" \
  -reducer "python3 rating_count.py --step-num=0 --reducer" \
  -input /data/Electronics.json \
  -output /output_ratings
```

> **Note:** If re-running, delete the output directory first:
> ```bash
> docker exec -it namenode hdfs dfs -rm -r /output_ratings
> ```

### 6. View the Results

```bash
docker exec -it namenode hdfs dfs -cat /output_ratings/part-00000
```

---

## 🔧 MapReduce Logic (`rating_count.py`)

```python
# Mapper emits:  (rating_value, 1)
# Reducer sums:  (rating_value, total_count)
```

Each JSON review line is parsed, the `overall` field (rating 1–5) is extracted as the key, and a count of `1` is emitted. The reducer sums all counts per rating key, producing 5 output records.

---

## ⚙️ Hive Setup (Optional)

Hive was configured inside the namenode for SQL-layer exploration.

```bash
# Initialize schema
$HIVE_HOME/bin/schematool -dbType derby -initSchema

# Launch Hive shell
hive

# Create database and table
CREATE DATABASE amazon_reviews_db;
USE amazon_reviews_db;

CREATE TABLE electronic_reviews (
  reviewerID STRING, asin STRING, reviewerName STRING,
  helpful_votes INT, review_text STRING, overall FLOAT,
  summary STRING, unix_time BIGINT, review_time STRING
) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' STORED AS TEXTFILE;
```

---

## 🐞 Challenges & Fixes

| Challenge | Fix |
|-----------|-----|
| HDP 3.0.1 Sandbox too large (15GB, 30+ min deploy) | Switched to `apache/hadoop:3` — deployed in under 5 min |
| Hive `schematool` Guava version conflict | Replaced Hive's Guava jar with Hadoop's newer version |
| `apt-get install python3` failing (Debian Stretch EOL) | Pointed apt sources to `archive.debian.org` |
| HDFS output directory conflict on reruns | Run `hdfs dfs -rm -r /output_ratings` before each job |

---

## 📚 Dataset

- **Source:** [Amazon Product Reviews v2 — Electronics](https://cseweb.ucsd.edu/~jmcauley/datasets/amazon_v2/)
- **Format:** JSON Lines (one review object per line)
- **Key field used:** `overall` (float, values 1.0–5.0)

---

## 👤 Author

**Samruddhi Chitnis**  
[github.com/samruddhichitnis02](https://github.com/samruddhichitnis02)

**Anushka Khadatkar**  
[github.com/AnushkaKhadatkar](https://github.com/AnushkaKhadatkar)
