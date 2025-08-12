# MLOps

https://campus.datacamp.com/courses/mlops-concepts/  
https://datacamp.com/blog/getting-started-with-mlops  


- definition: set of tools, practices, techniques, culture, and mindset that ensure reliable and scalable deployment of ml systems  
- mlops has emerged over the past few years with the aim of solving the deployment challenges data teams face
- benefits: speed, reliability and security, improved collaboration 

- lifecycle: design, develop, deploy  
    - during each phase, it is important to constantly evaluate with stakeholders whether the machine learning project should be continued.
    - it's a high-level overview of how a machine learning project should be structured in order to deliver real, practical value.

### Design

  * problem definition and requirements
    - manual process, speed up by using templates
    - describe context of problem
    - describe added value (estimate potential value of ml project)
    - describe business requirement (e.g., accuracy, freq and speed of outcome, transparency, explainabilty)
  * exploratory data analysis
    - data understanding; serves as input for data quality checks and feature engineering
    - key metrics (e.g., accuracy, customer happiness, monitory value)
    - data processing (quality data to build ml model on?)
      - accuracy
      - completeness
      - consistency / similar definitions
      - timeliness / when available
  * implementation design
    - design data pipeline; try to limit footprint, do as much prep work in dwh

###  Development

  * feature engineering
    - watch out for over engineering / noise
    - if possible, use feature store
  * experiment design
  * model training and evaluation
    - if possible, create sklearn pipelines couples data prep to model training
    - store model.pck itself (mlflow)
    - store metadata of trained models (mlflow):
        - how the input data is obtained
        - the parameters that define splitting the data in training and holdout sets
        - the parameters that define the model itself (shap)
        - the parameters that define the training process
        - the results of the evaluation against the holdout set (evaluation plots)
    
### Deployment

  * ci/cd
      - ci = changes are continuously integrated and tested quickly and frequently
      - cd = automating the release of the code that was validated during ci
  * deploy
    - three strategies:
      - basic strategy = simply overwrite model
      - shadow deployment = 50% of data to new
      - canery deployment = 10% of data + upscale if it works
    - containerization: easy to create copies of app in different env + improve scalability
    - ci/cd: automate and speed up development and deployment
    - microservices: scalable + independent development and deployment
  * monitor
      - statistical monitoring = input and output data
          - data drift = shift in input data
          - concept drift = change in feature impact
          - retrain model when data/concept drift or model performance drops below business requirements threshold
      - computational monitoring = request, uptime, cpu load, ...
      - feedback loop: predictions vs ground truth
  - integrate ml model into business process
  - deploy in prd

### Maturity scan Eneco

- business ownership
- model dashboard ownership
- data pipelines ownership
- monitoring ogsm contribution amount vs optimal
- scalable
- roadmap / backlog in place
- end of life check
- monitoring statistical / computational in place
- warning system in place
- platform envs
- performance time ok
- governance: definitions ok
- prd automated
- prd documented
