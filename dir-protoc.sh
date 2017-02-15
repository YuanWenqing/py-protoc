#!/bin/bash
set -e

workDir=`cd "$(dirname "$0")"; pwd`
echo "* enter into $workDir"
cd $workDir

protoDir=./example/proto
protoModule=./example/out/backend
srcDir=$protoModule/src/main/java/
resDir=$protoModule/src/main/resources

grpcPlugin=./plug/protoc-gen-grpc-java-0.13.2-osx-x86_64

if [[ "$OSTYPE" == "linux-gnu" ]]; then
  grpcPlugin=./plug/protoc-gen-grpc-java-0.13.2-linux-x86_64
# elif [[ "$OSTYPE" == "darwin"* ]]; then
#   grpcPlugin=plug/protoc-gen-grpc-java-0.13.2-osx-x86_64
fi

# rm old and mkdir
echo "* clear old and prepare for new"
if [ -d $srcDir ]; then
  rm -r $srcDir
fi
if [ -d $resDir ]; then
  rm -r $resDir
fi
mkdir -p $srcDir $resDir

version=`cd $protoDir; git rev-parse HEAD`
verFile=$resDir/proto.version

models=()
function recurseDir() {
  for file in `ls $1`
  do
    if [ "$file" == "rpc" ]; then
      continue
    fi
    path=$1"/"$file
    if [ -d $path ]; then
      recurseDir $path
    else
      models+=($path)
    fi
  done
}

models=()
recurseDir $protoDir

echo "* compile data model..."
for path in ${models[@]}
do
  echo ". compiling $path ..."
  protoc --proto_path=$protoDir --java_out=$srcDir $path
done

models=()
recurseDir "$protoDir/rpc"

echo "* compile grpc model..."
for path in ${models[@]}
do
  echo ". compiling $path ..."
  protoc --proto_path=$protoDir --plugin=protoc-gen-grpc-java=$grpcPlugin --grpc-java_out=$srcDir $path
done

echo "* proto version: $version"
echo ". write into $verFile"
echo "proto version: $version" > $verFile

echo "* [done] complied *.java located in $srcDir"
