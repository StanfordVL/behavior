FROM stanfordvl/behavior:latest
ENV PATH /miniconda/envs/gibson/bin:$PATH

ADD benchmark/agents/agent.py /agent.py
ADD benchmark/agents/random_agent.py /random_agent.py
ADD benchmark/agents/rl_agent.py /rl_agent.py
ADD benchmark/behavior_benchmark.py /behavior_benchmark.py

ADD benchmark/scripts/submission.sh /submission.sh
WORKDIR /
