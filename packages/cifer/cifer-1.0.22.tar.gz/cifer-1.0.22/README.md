<p align="left">
  <a href="https://cifer.ai/">
    <img src="https://cifer.ai/assets/themes/cifer/images/logo/ciferlogo.png" width="240" alt="Cifer Website" />
  </a>
</p>

Cifer is a **Federated Learning framework with integrated Fully Homomorphic Encryption (FHE)** for secure, decentralized model training and encrypted aggregation.

It improves model robustness, reduces bias, and handles distribution shift across non-IID data.

Supports both centralized and decentralized topologies by default, with optional Cifer Blockchain integration for auditability and provenance.

[![GitHub license](https://img.shields.io/github/license/CiferAI/ciferai)](https://github.com/CiferAI/ciferai/blob/main/LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/CiferAI/ciferai/blob/main/CONTRIBUTING.md)
[![Downloads](https://static.pepy.tech/badge/cifer)](https://pepy.tech/project/cifer)

[🌎 Website](https://cifer.ai) &nbsp;&nbsp;| &nbsp;
[📔 Docs](https://cifer.ai/documentation) &nbsp;&nbsp;| &nbsp;
[🙌 Join Slack](https://join.slack.com/t/cifertalk/shared_invite/zt-2y09cb0yu-zHYyNkiYWq6AfssvU2rLrA)

---
<br>

# Cifer Python Package (PyPI)

The cifer Python package provides a secure, programmatic interface for executing **Privacy-Preserving Machine Learning (PPML)** workflows. It enables local and distributed model training using **Federated Learning (FL)** and **Fully Homomorphic Encryption (FHE)**—without ever exposing raw data.

This package is ideal for Python developers, researchers, and data scientists who need fine-grained control over federated workflows within trusted or adversarial environments.

For alternative development workflows:

* Use the[ Cifer Python Package](https://pypi.org/project/cifer) for direct integration into custom Python-based ML pipelines
* Use[ Cifer Workspace](https://workspace.cifer.ai) for browser-based, no-code orchestration and collaborative workspace

---
<br>

# What is Cifer Federated Learning?

**Cifer Federated Learning (FedLearn)** is a secure training framework that enables collaborative machine learning across distributed data sources—without ever sharing raw data. Each participant (or node) performs local training, and only encrypted model updates are exchanged across the network.

Rather than centralizing data into a vulnerable repository, Cifer coordinates encrypted computations between participants, preserving **data sovereignty, compliance,** and **confidentiality** across jurisdictions and organizations.

## Key Extensions Beyond Standard FL

* **Fully Homomorphic Encryption (FHE)**\
  Cifer integrates FHE at the protocol level, allowing model updates and gradients to be computed on encrypted tensors. This ensures data remains encrypted throughout the lifecycle—including training, aggregation, and communication.\
  Unlike differential privacy (DP), which introduces noise and cannot fully prevent reconstruction attacks, FHE offers cryptographic guarantees against adversarial inference—even in hostile environments.\

* **Dual Topology Support: Centralized and Decentralized**\
  Cifer supports both:
  * **Client–Server (cFL):** A central coordinator aggregates updates from authenticated participants—ideal for trusted, enterprise-level deployments.
  * **Peer-to-Peer (dFL):** Participants can operate without a central aggregator, enabling direct encrypted update exchanges across nodes for higher resilience.\

* **Secure Communication Channels**\
  All communication is conducted over **gRPC**, leveraging **HTTP/2** and Protocol Buffers for efficient, multiplexed, and encrypted transport. This ensures fast synchronization while minimizing attack surfaces.\

* **Blockchain Integration** (Optional)\
  For use cases requiring immutable audit trails, decentralized identity, or consensus-based coordination, Cifer supports integration with its proprietary **Cifer Blockchain Network**, providing an additional layer of provenance and tamper resistance.

## Federated Learning and the Adversarial Threat Model

Standard federated learning protocols are susceptible to:

* Gradient leakage and model inversion attacks
* Malicious participant injection
* Data reconstruction through side-channel inference

The industry trend has been to use differential privacy (DP) to mitigate these threats. However:

* DP requires complex tuning of privacy budgets (ε, δ)
* It introduces statistical noise, reducing model accuracy
* It provides probabilistic—not cryptographic—guarantees, and can still leak information under repeated queries or cumulative exposure\


Cifer’s FHE-based design **eliminates these risks** by ensuring that all shared model artifacts remain mathematically unreadable, even under active attack or node compromise.

## Performance Capacity

Cifer FedLearn is built for real-world scale:

* Supports **client-server and P2P** topologies
* Tested for **model sizes and parameter transfers up to 30GB**
* Optimized for **GPU acceleration, NUMA-aware compute,** and **multi-node orchestration**

## Core Modules

* **FedLearn**\
  Orchestrates decentralized training across multiple nodes while maintaining data locality. Supports both:
  * **Centralized FL (cFL)** for governed, trusted environments
  * **Decentralized FL (dFL)** with peer coordination across encrypted channels
* **HomoCryption (FHE)**\
  Allows computation on encrypted data throughout the training lifecycle, preserving privacy even during intermediate operations.

## Key Capabilities

* **Hybrid Federation Support**\
  Choose between cFL or dFL architectures depending on governance, trust, and fault tolerance requirements.
* **Secure Communication Protocol**\
  Powered by gRPC with HTTP/2 and Protocol Buffers:
  * Low-latency streaming
  * Compact serialized messages
  * Built-in encryption and authentication
* **End-to-End Encrypted Computation**\
  FHE is embedded directly into the training workflow. No intermediate decryption. Data privacy is mathematically guaranteed.\

---
<br>

# Before Getting Started

To ensure a smooth experience using Cifer for Federated Learning (FL) and Fully Homomorphic Encryption (FHE), please verify your system meets the following baseline requirements:

## System Requirements

* **Operating System**
  * Linux (Ubuntu 18.04 or later)
  * macOS (10.14 or later)
  * Windows 10 or later
* **Python**
  * Version: 3.9 (only version officially supported)
* **Memory**
  * Minimum: 8 GB RAM
  * Recommended: 16 GB+ for large-scale training or encryption tasks
* **Storage**
  * At least 30 GB of available disk space
* **Network**
  * Stable internet connection (required for remote collaboration or coordination modes)

## GPU Acceleration (Optional)

Cifer supports GPU acceleration for both FL and FHE components using:

* **NVIDIA CUDA** (for TensorFlow, PyTorch pipelines)
* **Google TPU** (via JAX and compatible backends)

While GPU is not mandatory, it is highly recommended for encrypted training at scale or production-grade deployments.

---
<br>

# Getting Started with Cifer’s Federated Learning

Cifer provides a modular Federated Learning (FL) framework that enables privacy-preserving model training across distributed environments. To get started, install the package via pip, import the required modules, and choose your preferred communication method for orchestration.

## What's Included in pip install cifer

Installing Cifer via pip provides the following components and features:

### **Core Modules**

* **FedLearn:** Federated learning engine for decentralized model training.
* **HomoCryption:** Fully Homomorphic Encryption (FHE) for computation on encrypted data.

**Integrations**

* **Built-in compatibility with** TensorFlo&#x77;**,** PyTorch, scikit-learn, NumPy, CUDA, JAX, Hugging Face Transformers.

**Utilities**

* Data preprocessing tools
* Privacy-preserving metrics
* Secure aggregation algorithms

**Cryptographic Libraries**

* Integration with advanced homomorphic encryption backends

**Communication Layer**

* gRPC-based secure communication protocols for FL orchestration

**Command-Line Interface (CLI)**

* CLI client for managing experiments and configurations

**Example Notebooks**

* Jupyter notebooks demonstrating end-to-end workflows

## **Optional Dependencies**

Install extras using:

```python
pip install cifer[extra]
```

Options:

* viz: Visualization tools
* gpu: GPU acceleration support
* all: Installs all optional dependencies

---
<br>

# 1. Install Cifer

```bash
pip install cifer
```

To include all optional features:

```python
pip install cifer[all]
```

---
<br>

# 2. Import Required Modules

```python
from cifer import fedlearn as fl
```

---
<br>

# 3. Choose a Communication Method

Cifer supports two communication modes for FL orchestration:

## **Method A: gRPC Client with JSON Configuration**

Connect to a remote Cifer server via gRPC using a JSON config file.

* Best for: Quick onboarding, lightweight setup, connecting to Cifer Workspace backend.
* Setup: Supply a JSON file with encoded credentials and project parameters.
* No server deployment required—ideal for minimal infrastructure environments.

```json
{
 base_api="http://localhost:5000",
 "port": 8765,
 "n_round_clients": 2,
 "use_homomorphic": true,
 "use_secure": true,
 "certfile": "certificate.pem",
 "keyfile": "private_key.pem"
}
```

## **Method B: Self-Hosted WebSocket Server**

Deploy your own FL coordination server using WebSocket (WSS).

* **Best for:** On-premise, private environments or regulated sectors.
* **Setup:** Launch your own server and connect clients within the same secure channel.

```json
{
 "ip_address": "wss://0.0.0.0",
 "port": 8765,
 "n_round_clients": 2,
 "use_homomorphic": true,
 "use_secure": true,
 "certfile": "certificate.pem",
 "keyfile": "private_key.pem"
}

```

---
<br>

# 4. Define Your Dataset and Base Model

This is where users prepare their local training environment before initiating any FL round.

## Define Dataset

You must prepare and point to a local dataset for training. Cifer expects standardized input for consistency across participants.

* **Supported formats:** NumPy (.npy, .npz), CSV, or TFRecords
* **Recommended:** Preprocess and normalize data before training

```
dataset_path = "YOUR_DATASET_PATH"
```

## Define Base Model

You can define your ML model in three ways: using a local file, cloning from GitHub, or downloading from Hugging Face.

### **Option 1: Create Model Locally**

```
model_path = "YOUR_MODEL_PATH"
```

### **Option 2: Load Model from GitHub**

Clone the model repository and point to the .h5 or .pt file.

```
git clone https://github.com/example/model-repo.git models/
```

Then specify:

```
model_path = "models/your_model.h5"
```

### **Option 3: Load Pretrained Model from Hugging Face**

Install transformers if needed:

```
pip install transformers
```

Download and configure:

```
from transformers import AutoModel
model_path = "models/huggingface_model"
model = AutoModel.from_pretrained("bert-base-uncased")
model.save_pretrained(model_path)
```

Then reference:

```
model_path = "models/huggingface_model"
```

---
<br>

# 5. Start the Training Process

Once your dataset and base model are defined, you can initialize the federated learning process. Cifer supports both server (Fed Master) and client (Contributor) roles depending on your deployment mode.

## Method A: gRPC Client with JSON Configuration

This method is ideal if you're using Cifer's hosted infrastructure (via Cifer Workspace) and want to avoid setting up your own server.

### **1. Prepare JSON Configuration**

Create a config.json file with the following structure:

```json
{
 "ip_address": "https://localhost",
 "port": 5000,
 "n_round_clients": 2,
 "use_homomorphic": true,
 "use_secure": true,
 "certfile": "certificate.pem",
 "keyfile": "private_key.pem"
}
```

### 2. Start Training

```python
from cifer import CiferClient
client = CiferClient(config_path="config.json")
client.run()
```

This connects the client to Cifer’s gRPC backend, performs local training, and submits encrypted model updates.

## Method B: Self-Hosted WebSocket Server

Use this method if you want full control over orchestration and deployment, or if you need to run the system entirely on-premise.

### **Server: Launch Aggregation Coordinator**

```python
from cifer import fedlearn as fl

server = fl.Server()
strategy = fl.strategy.FedAvg(
    data_path="dataset/mnist.npy",
    model_path="model/mnist_model.h5"
)

server.run(strategy)
```

### Client: Start Local Training

```python
from cifer import CiferClient

client = CiferClient(
    encoded_project_id="YOUR_PROJECT_ID",
    encoded_company_id="YOUR_COMPANY_ID",
    encoded_client_id="YOUR_CLIENT_ID",
    base_api="wss://yourserver.com",
    dataset_path="dataset/mnist.npy",
    model_path="model/mnist_model.h5"
)

client.run()
```

> ⚠️ Ensure that your WebSocket server is reachable via a wss:// secure connection.

Both methods will iteratively perform local training, encrypted aggregation, and global model updates across multiple rounds.

---
<br>

# 6. Aggregation Process

Federated Aggregation is the core of Cifer’s coordination loop—where encrypted model updates from clients are securely combined into a global model.

## Method A: gRPC with JSON Configuration (Cifer Workspace)

When using the gRPC method (via CiferClient), aggregation is automatically handled by Cifer's managed infrastructure.

* No manual aggregation code is required.
* After each client sends its local update, the server:
  * Decrypts (if FHE is enabled)
  * Aggregates using the selected strategy (e.g., FedAvg, FedSGD)
  * Sends back the updated model to each client

> Best for teams who want rapid onboarding with minimal infra overhead.

**To customize strategy:** Contact the Cifer Workspace team to enable custom orchestration logic.

## Method B: Self-Hosted WebSocket Server

When running your own aggregation server, you have full control over the aggregation algorithm.

Example using FedAvg:

```python
from cifer import fedlearn as fl

server = fl.Server()
strategy = fl.strategy.FedAvg(
    data_path="dataset/mnist.npy",
    model_path="model/mnist_model.h5"
)

server.run(strategy)
```

You may substitute `FedAvg` with other strategies (e.g., `FedProx`, `FedYogi`) or define your own:

```python
class CustomAggregation(fl.strategy.BaseStrategy):
    def aggregate(self, updates):
        # implement custom logic
        return aggregated_model

strategy = CustomAggregation()
server.run(strategy)
```

* If FHE is enabled, aggregation will happen on encrypted tensors. Ensure your aggregation strategy supports homomorphic operations (e.g., addition, averaging).
* Full FHE documentation is provided in a later section.

## Monitoring Aggregation

For both methods:

* Aggregation rounds run until the configured number of epochs or convergence is reached.
* Logs for each round (loss, accuracy, gradient stats) are available via CLI or Jupyter Notebook (in CLI or Workspace mode).
* You can visualize training progress using Cifer’s optional viz module:

```
pip install cifer[viz]
```

## Aggregation with WebSocket Server (Method B)

If you're running a self-hosted WebSocket server (wss://), aggregation must be explicitly defined and handled in your orchestration logic.

```python
from cifer import fedlearn as fl
server = fl.Server()
strategy = fl.strategy.FedAvg(
    data_path="/path/to/data",
    model_path="/path/to/model"
    # Optionally: encryption=True if using FHE
)
server.run(strategy)
```

FedAvg is the default aggregation strategy. You may replace it with any supported method (e.g., `FedProx`, `SecureFed`).

When using FHE, make sure your aggregation method only uses additive-compatible operations.

This method gives full control over server lifecycle, custom hooks, and logging.

---
<br>

# Getting Started with Cifer’s Homomorphic Encryption (FHE)

Cifer includes a built-in homocryption module for Fully Homomorphic Encryption (FHE), allowing computation on encrypted tensors without exposing raw data. You can encrypt, perform arithmetic, relinearize, and decrypt—all while preserving confidentiality.

## 1. Import HomoCryption Module

```python
from cifer.securetrain import (
   generate_named_keys,
   encrypt_dataset,
   train_model,
   decrypt_model,
)
```

## 2. Generate Keys

```bash
def generate_named_keys(key_name):
   print(f"🔐 Generating public/private key pair for: {key_name}")
   pubkey, privkey = paillier.generate_paillier_keypair()
   dir_path = f"keys/{key_name}"
   os.makedirs(dir_path, exist_ok=True)
   with open(os.path.join(dir_path, "public.key"), "wb") as f:
       pickle.dump(pubkey, f)
   with open(os.path.join(dir_path, "private.key"), "wb") as f:
       pickle.dump(privkey, f)
   print(f"✅ Keys saved to: {dir_path}/public.key, {dir_path}/private.key")
   return pubkey, privkey
```

## 3. Encrypt Data

```bash
pubkey, _ = generate_named_keys(key_name)
   print("🔐 Encrypting dataset...")
   enc_df = df.copy()
   for col in enc_df.columns:
       enc_df[col] = enc_df[col].apply(lambda x: pubkey.encrypt(x))

   os.makedirs(os.path.dirname(output_path), exist_ok=True)
   print(f"💾 Saving encrypted dataset to: {output_path}")
```

## 4. Perform Encrypted Computation

Example: Add two encrypted values

```bash
privkey = load_private_key(key_name)

   try:
       X_plain = np.array([[privkey.decrypt(val) for val in row] for row in X_enc])
       y_plain = np.array([privkey.decrypt(val) for val in y_enc])
   except Exception as e:
       print(f"❌ Failed to decrypt: {e}")
       return

   print("✅ Label distribution:", np.unique(y_plain, return_counts=True))
   if len(np.unique(y_plain)) < 2:
       print("❌ Need at least 2 classes in the dataset for training.")
       return

   print("🧠 Training model using decrypted values...")
   clf = LogisticRegression()
   clf.fit(X_plain, y_plain)

   print(f"💾 Saving trained model to: {output_model_path}")
```

Apply relinearization to manage ciphertext noise:

```bash
# Encrypt two vectors
vec1 = ts.ckks_vector(context, [1.0, 2.0, 3.0])
vec2 = ts.ckks_vector(context, [4.0, 5.0, 6.0])

# Multiply and relinearize
encrypted_result = vec1 * vec2
encrypted_result.relinearize()  # 👈 This is the relinearize step
decrypted = encrypted_result.decrypt()
```

## 5. Decrypt Result

```bash
with open(encrypted_path, "rb") as f:
       enc_df = pickle.load(f)

   print("🔄 Extracting features and labels...")
   try:
       X_enc = enc_df[feature_cols].values.tolist()
       y_enc = enc_df[label_col].values.tolist()
   except KeyError as e:
       print(f"❌ Column error: {e}")
       return

   print(f"📂 Loading private key to decrypt data for training: {key_name}")
   privkey = load_private_key(key_name)
   
   try:
       X_plain = np.array([[privkey.decrypt(val) for val in row] for row in X_enc])
       y_plain = np.array([privkey.decrypt(val) for val in y_enc])
   except Exception as e:
       print(f"❌ Failed to decrypt: {e}")
       return

   print("✅ Label distribution:", np.unique(y_plain, return_counts=True))
   if len(np.unique(y_plain)) < 2:
       print("❌ Need at least 2 classes in the dataset for training.")
       return

   print("🧠 Training model using decrypted values...")
   clf = LogisticRegression()
   clf.fit(X_plain, y_plain)

   print(f"💾 Saving trained model to: {output_model_path}")
```

| **Operation**  | **Method**         | **Compatible with Aggregation** |
| -------------- | ------------------ | ------------------------------- |
| Addition       | `hc.add()`         | ✅ Yes                           |
| Multiplication | `hc.mul()`         | ⚠️ Partially (check noise)      |
| Relinearize    | `hc.relinearize()` | ✅ Required after `mul()`        |
| Decryption     | `hc.decrypt()`     | 🔐 Private key required         |

---
<br>

# FHE in Aggregation Context

When using FHE-enabled federated learning:

* Each client encrypts model weights before sending
* The server performs aggregation (e.g., summing encrypted tensors)
* Final decryption happens at a trusted node after aggregation
* Only compatible operations (addition, averaging) are supported

> ⚠️ If FHE is enabled, make sure your aggregation strategy supports encrypted arithmetic.

---
<br>

# Learn More

For detailed examples, deployment patterns, and advanced configurations:

* Full documentation:[ https://www.cifer.ai/docs](https://www.cifer.ai/docs)
* GitHub repository:[ https://github.com/ciferai/cifer](https://github.com/ciferai/cifer)
* Developer support: support@cifer.ai
