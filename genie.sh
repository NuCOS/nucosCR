#!/bin/bash
PACKAGE=nucosCR
VENV=./venv
if [ -d "$VENV" ]; then
  echo "remove virtual env first"
  sleep 2
  rm -rf "$VENV"
fi


###################################
echo "----------------------------------------------------"
{
conda create --name $PACKAGE'3_5' python=3.5 -y
source activate $PACKAGE'3_5'
} || { 
virtualenv -p $(which python3) $VENV/py3
source $VENV/py3/bin/activate 
}
pip install --upgrade pip
pip install nose2
python setup.py sdist

###################################
echo "----------------------------------------------------"
sleep 1
echo "python used: "
which python
python info.py
###################################
echo "----------------------------------------------------"
sleep 1
echo "now install the nucosCR in python 3"
python setup.py install
####################################
echo "----------------------------------------------------"
sleep 1
echo "now run test in py3"
nose2 --plugin nose2.plugins.junitxml --junit-xml
python aftermath.py nose2-junit.xml py3
echo "test done in:"
python info.py
sleep 3

source deactivate
echo "after deactivate"
python info.py
sleep 3
###################################
echo "----------------------------------------------------"
{
conda create --name $PACKAGE'2_7' python=2.7 -y
source activate $PACKAGE'2_7'
} || {
virtualenv -p $(which python2) venv/py2
source $VENV/py2/bin/activate
}

pip install --upgrade pip
pip install nose2
python setup.py sdist
###################################
echo "----------------------------------------------------"
sleep 1
echo "python used: "
which python
python info.py
###################################
echo "----------------------------------------------------"
sleep 1
echo "now install the nucosCR"
python setup.py install
####################################
echo "----------------------------------------------------"
sleep 1
echo "now run test in py2"
nose2 --plugin nose2.plugins.junitxml --junit-xml
python aftermath.py nose2-junit.xml py2
echo "test done in:"
python info.py
sleep 1


#sleep 1
#echo "deactivate"
#source deactivate
