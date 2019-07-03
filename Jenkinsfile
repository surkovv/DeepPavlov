node('gpu') {
    timestamps {
        try {
            stage('Clean') {
                sh "rm -rf .[^.] .??* *"
            }
            stage('Checkout') {
                sh "cp -r ${pwd()}@script/* ."
            }
            stage('Setup') {
                env.TFHUB_CACHE_DIR="tfhub_cache"
                env.LD_LIBRARY_PATH="/usr/local/cuda-9.0/lib64"
                sh """
                    virtualenv --python=python3 '.venv-$BUILD_NUMBER'
                    . '.venv-$BUILD_NUMBER/bin/activate'
                    pip install .[tests,docs]
                    pip install -r deeppavlov/requirements/tf-gpu.txt
                    rm -rf `find . -mindepth 1 -maxdepth 1 ! -name tests ! -name Jenkinsfile ! -name docs ! -name '.venv-$BUILD_NUMBER'`
                """
            }
            stage('Tests') {
                sh """
                    . .venv-$BUILD_NUMBER/bin/activate
                    flake8 `python -c 'import deeppavlov; print(deeppavlov.__path__[0])'` --count --select=E9,F63,F7,F82 --show-source --statistics
                    pytest -v --disable-warnings
                    cd docs
                    make clean
                    make html
                """
                currentBuild.result = 'SUCCESS'
            }
        }
        catch(e) {
            currentBuild.result = 'FAILURE'
            throw e
        }
        finally {
            emailext to: '${DEFAULT_RECIPIENTS}',
                subject: "${env.JOB_NAME} - Build # ${currentBuild.number} - ${currentBuild.result}!",
                body: '${BRANCH_NAME} - ${BUILD_URL}',
                attachLog: true
        }
    }
}
