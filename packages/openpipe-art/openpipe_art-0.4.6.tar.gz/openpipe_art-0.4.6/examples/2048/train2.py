import asyncio
import os
import random

# from dotenv import load_dotenv
from rollout import rollout

import art
from art import TrainableModel
from art.rewards import ruler_score_group
from art.skypilot.backend import SkyPilotBackend

random.seed(42)

# weave.init("2048")

model = TrainableModel(
    name="agent-003",
    project="2048",
    base_model="Qwen/Qwen2.5-3B-Instruct",
)

model._internal_config = art.dev.InternalModelConfig(
    init_args=art.dev.InitArgs(
        max_seq_length=8192,  # need this long for longer games.
    ),
    engine_args=art.dev.EngineArgs(
        enforce_eager=False,  # Enable CUDA graphs for better performance
        gpu_memory_utilization=0.8,  # Conservative memory usage
    ),
    trainer_args=art.dev.TrainerArgs(
        per_device_train_batch_size=1,
        gradient_accumulation_steps=1,
    ),
)

TRAIN_STEPS = 40
SIMULTANEOUS_GAMES = 8
ENABLE_RULER = True


async def main():
    backend = await SkyPilotBackend.initialize_cluster(
        cluster_name="art-cluster1", gpu="H100", env_path=".env"
    )

    await model.register(backend)

    for i in range(await model.get_step(), TRAIN_STEPS):
        train_trajectories = await art.gather_trajectory_groups(
            (
                art.TrajectoryGroup(
                    rollout(model, i, is_validation=False)
                    for _ in range(SIMULTANEOUS_GAMES)
                )
                for _ in range(1)
            ),
            after_each=lambda group: (
                ruler_score_group(
                    group,
                    "azure/gpt4o",
                    extra_litellm_params={
                        "temperature": 0.4,  # default is 1.0 by LiteLLM
                        "api_base": os.getenv("AZURE_OPENAI_ENDPOINT"),
                        "api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
                        "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
                    },
                    debug=True,
                    swallow_exceptions=True,  # Return None on error, filtering out the group?
                )
            ),
            pbar_desc="gather",
            max_exceptions=10,
        )

        await model.train(
            train_trajectories,
            config=art.TrainConfig(learning_rate=1e-5),
        )

        await backend.down()


if __name__ == "__main__":
    asyncio.run(main())
