# 🌥️ cloud-resume-challenge

Welcome to my repository for the Cloud Resume Challenge Bootcamp (Q4 2025) organized by ExamPro.
Here you’ll find **Terraform** files, **GitHub Actions** workflows, **Python** applications, diagrams, resume's website files and complete documentations to setup and deploy a working Cloud Resume Challenge using different cloud providers (only the Azure version is available for now).

## 🗒️ Sections

- [Frontend Technical Specifications](./frontend/README.md)
- [Azure Version for the Cloud Resume Challenge](./azure/README.md)
  - [Writing and Deploying the Cloud Resume Challenge's Frontend](./azure/frontend-resources/README.md)
  - [Writing and Deploying the Cloud Resume Challenge's Backend](./azure/backend-resources/README.md)

## 🗂️ Repository Structure

```txt
.
├── .github/
│   └── workflows/
│       ├── deploy-backend.yml
│       └── deploy-frontend.yml
├── azure/
│   ├── README.md
│   ├── backend-resources/
│   │   ├── .gitignore
│   │   ├── .terraform.lock.hcl
│   │   ├── README.md
│   │   ├── create-entity-module/
│   │   │   ├── create_entity.py
│   │   │   └── requirements.txt
│   │   ├── images/
│   │   ├── main.tf
│   │   ├── provider.tf
│   │   ├── terraform.tf
│   │   ├── variables.tf
│   │   └── visitor-counter/
│   │       ├── function_app.py
│   │       ├── host.json
│   │       └── requirements.txt
│   └── frontend-resources/
│       ├── .gitignore
│       ├── .terraform.lock.hcl
│       ├── README.md
│       ├── images/
│       ├── main.tf
│       ├── provider.tf
│       ├── terraform.tf
│       └── variables.tf
├── frontend/
│   ├── README.md
│   └── resume/
│       ├── index.html
│       ├── docs/
│       │   └── images/
│       └── src/
│           ├── images/
│           │   └── (logo and certification images)
│           ├── styles/
│           │   ├── styles.css
│           │   └── fonts/
│           └── visitor-counter/
│               └── visitor-counter.js
├── README.md
└── .gitignore
```

## 📌 How to Use This Repo

1. **Clone & explore**:

    ```sh
    git clone https://github.com/vegasjj/cloud-resume-challenge.git
    cd cloud-resume-challenge
    ```

2. **Read walkthroughs and notes**: For notes, steps taken and troubleshooting follow the relevant links in [Sections](#️-sections).
