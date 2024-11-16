# B-Hunters-Dirsearch

**This is the module that is responsible for Web path discovery in [B-Hunters Framework](https://github.com/B-Hunters/B-Hunters) using [dirsearch](https://github.com/maurosoria/dirsearch).**


## Requirements

To be able to use all the tools remember to update the environment variables with your API keys in `docker-compose.yml` file as some tools will not work well until you add the API keys.

## Usage 

**Note: You can use this tool inside [B-hunters-playground](https://github.com/B-Hunters/B-Hunters-playground)**   
To use this tool inside your B-Hunters Instance you can easily use **docker-compose.yml** file after editing `b-hunters.ini` with your configuration.

# 1. **Build local**
Rename docker-compose.example.yml to docker-compose.yml and update environment variables.

```bash
docker compose up -d
```

# 2. **Docker Image**
You can also run using docker image
```bash
docker run -d  -e deepscan=False -e max_threads=400 -v $(pwd)/b-hunters.ini:/etc/b-hunters/b-hunters.ini bormaa/b-hunters-dirsearch:v1.0
```

## How it works

B-Hunters-Dirsearch receives the Paths from different B-Hunters modules 
![B-Hunters_Dirsearch](https://i.imgur.com/GG3Jxc0.png)

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/bormaa)
