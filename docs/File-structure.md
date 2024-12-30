# Project File Structure and Key Files

## Project File Structure
```
custom-nlp-chatbot/
├── data/
│   ├── raw/                     # Raw text data for model training
│   ├── processed/               # Cleaned and preprocessed text data
│   ├── financial_datasets/      # Financial datasets for fine-tuning
│   ├── support_datasets/        # Customer support datasets
│   └── validation/             # Data validation and quality checks
├── models/
│   ├── base_model/             # Pre-trained base model
│   ├── fine_tuned_financial_model/
│   ├── fine_tuned_support_model/
│   ├── tokenizer/              # Tokenizer configuration
│   └── experiments/            # MLflow or W&B experiment tracking
├── knowledge_graphs/
│   ├── financial_kg/           # Financial entities knowledge graph
│   └── support_kg/            # Support processes knowledge graph
├── src/
│   ├── api/                    # FastAPI implementation
│   │   ├── routes/
│   │   ├── middleware/
│   │   └── schemas/
│   ├── monitoring/            # Metrics and logging
│   ├── security/             # Security implementations
│   ├── cache/               # Caching logic
│   ├── chatbot.py
│   ├── model_training.py
│   ├── data_pipeline.py
│   ├── nlp_utils.py
│   ├── response_generator.py
│   ├── context_manager.py
│   └── real_time_data_integration.py
├── config/
│   ├── model_config.yaml
│   ├── deployment_config.yaml
│   └── api_keys.yaml
├── deployment/
│   ├── Dockerfile
│   ├── k8s_deployment.yaml
│   ├── CI-CD_pipeline.yaml
│   └── api_integration.yaml
├── tests/
│   ├── test_chatbot.py
│   ├── test_data_pipeline.py
│   ├── test_model_training.py
│   ├── test_response_generator.py
│   └── test_context_manager.py
```

## Key Files and Their Roles

### Core Application Files
1. **src/chatbot.py**
   - Main chatbot implementation
   - Connects to: api/routes, response_generator.py, context_manager.py

2. **src/api/main.py**
   - FastAPI application entry point
   - Connects to: all API routes and middleware

3. **src/response_generator.py**
   - Handles response generation logic
   - Connects to: financial/support models, knowledge graphs

4. **src/context_manager.py**
   - Manages conversation context
   - Connects to: chatbot.py, response_generator.py

### Data Processing Files
1. **src/data_pipeline.py**
   - Handles data ingestion and preprocessing
   - Connects to: data/ directories, model_training.py

2. **src/model_training.py**
   - Model training and fine-tuning
   - Connects to: data_pipeline.py, models/ directories

### API Implementation Files
1. **src/api/routes/financial.py**
   - Financial API endpoints
   - Connects to: financial model, real-time data integration

2. **src/api/routes/support.py**
   - Support API endpoints
   - Connects to: support model, knowledge graphs

### Security and Monitoring
1. **src/security/auth_handler.py**
   - Authentication and authorization
   - Connects to: all API routes

2. **src/monitoring/metrics_collector.py**
   - Performance monitoring
   - Connects to: all core components

### Configuration Files
1. **config/model_config.yaml**
   - Model configuration
   - Used by: model_training.py, chatbot.py

2. **config/deployment_config.yaml**
   - Deployment settings
   - Used by: Dockerfile, k8s_deployment.yaml

### Deployment Files
1. **deployment/Dockerfile**
   - Container configuration
   - Connects to: all application components

2. **deployment/k8s_deployment.yaml**
   - Kubernetes deployment configuration
   - Connects to: Dockerfile, CI-CD_pipeline.yaml
