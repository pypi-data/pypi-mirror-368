from golpo.client import Golpo
import time 

golpo_client = Golpo(api_key='96gkPmRejr1nLClgLpxHc3YlfpBP8IsW6Ptom6mT')

start_time = time.time()
podcast_url, podcast_script = golpo_client.create_video(
    prompt="summarize",
    new_script="hi, my name is shreyas",
    include_watermark=False
)
end_time = time.time()
print(f'time elapsed {end_time - start_time}')
print("******")
print(podcast_url)
print("********")
print(podcast_script)
print("**********")
