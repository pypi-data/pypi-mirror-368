## m(achine) l(earning) t(emplate)

## getting started  

1.) setup your development environment; consider using [github](https://github.com) to host your repo, [github cli](https://cli.github.com) to manage your repo using the command line, [github actions](https://github.com/features/actions) to manage your CI/CD pipeline, and [github issues](https://github.com/features/issues) to manage your project's progress.

2.) check the provided files and adjust if needed; check LICENSE, the workflows in the .github folder, config.yml for run configurations, Makefile for useful targets, and the docs folder for useful documentation.

3.) create a .env file with credentials needed in your project. Make sure your .env or other credentials are in the .gitignore file.

4.) create your virtual env; check the `make env` target in the Makefile. Note that the deep learning libraries are not installed by dafault.

5.) check the tests folder, create additional test if needed, and run `make test` to pytest the project and get the coverage report.

6.) setup your remote repo and push initial commit, see git.md in docs for more info on using git.zz

7.) run a train_ python file in the scripts folder to test your setup; check the `make run` target in the Makefile.

8.) check results including the shap analysis in mlflow.

9.) set your branch policies, create a feature branch and start working on your project; as a coding standard consider using black, isort, and flake8; this is included in the `make format` and `make lint` targets in the Makefile.
