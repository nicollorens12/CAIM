## How to run Elastic Search on macOS
### Requirements
Install ElasticSearch with:
```cmd
brew tap elastic/tap
brew install elastic/tap/elasticsearch-full
```
Java JDK is needed and ES_JAVA_HOME needs to be set
```cmd
nano ~/.zshrc
export ES_JAVA_HOME="$(brew --prefix openjdk)"
```

First start of ElasticSearch:
```cmd
brew services start elastic/tap/elasticsearch-full
```

On macOS (M Silicon):
```cmd
sudo nano /opt/homebrew/etc/elasticsearch/elasticsearch.yml
```
And add:
```cmd
xpack.ml.enabled: false
```

Restart service for apply changes:
```cmd
brew services restart elastic/tap/elasticsearch-full
```

You can now start elasticsearch server with:
```cmd 
elasticsearch
```

And check if the service is working with:
```cmd
curl -X GET "localhost:9200"
```
