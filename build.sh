#!/bin/bash
dir=$(pwd)
pub=$1


echo "Attempting to PyPi package"

echo "Remove old images"
mkdir dist
cd dist
rm *.gz -f
cd ..

echo "Adding git changes"
git add -A 

echo "Bumping Python patch version"
bumpversion patch --allow-dirty
if [[ $? -ne 0 ]]; then
    echo "in the wrong env?"
    exit 1
fi

echo "Build the package"
python setup.py sdist


if [[ ! -z "$pub" ]]; then
    echo "Upload the package"
    twine upload  dist/*
fi

mkdir test

echo "Updating test Environment"
cd test
pipenv install "$dir"
cd ..


echo "Done.."