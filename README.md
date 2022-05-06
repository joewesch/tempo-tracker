# Tempo Tracker

## Requires

- Atlassian User ID

> Log into Tempo/JIRA/Atlassian > Click on profile pic in top right > Profile. Your User ID is in the URI after `/jira/people/`

- Tempo API Key

> Log into Tempo > Settings (left side bar gear icon) > API Integration > New Token

## Docker

```
docker run -p 5000:5000 -e TEMPO_USER_ID=drxlonguserid -e TEMPO_TOKEN=drxlongtempotoken ghcr.io/joewesch/tempo-tracker
```

## Docker Compose

```yaml
  tempo_tracker:
    ports:
      - "5000:5000"
    environment:
      - TEMPO_USER_ID=drxlonguserid
      - TEMPO_TOKEN=drxlongtempotoken
    image: ghcr.io/joewesch/tempo-tracker
```

## Python

```
git clone https://github.com/joewesch/tempo-tracker.git
cd tempo-tracker
export TEMPO_USER_ID=drxlonguserid
export TEMPO_TOKEN=drxlongtempotoken
python tempo_tracker.py
``` 
