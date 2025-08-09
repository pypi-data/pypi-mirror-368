# Dataclass objects to specify parameters for the QEC experiment
# This includes the type of error correction code, distance,
# number of rounds, appropriate decoder to be used, noise model specification as Enums

from enum import Enum
from random import randint

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictBaseModel(BaseModel):
    """
    In pydantic v2, the base model allows extra fields by default.
    This custom base model forbids that
    """

    model_config = ConfigDict(extra="forbid")


class Code(str, Enum):
    """
    Enum representing different quantum error correction codes supported
    """

    ROTATEDSURFACECODE = "rotatedsurfacecode"
    REPETITIONCODE = "repetitioncode"
    STEANECODE = "steanecode"
    SHORCODE = "shorcode"

    @classmethod
    def _missing_(cls, value):
        # Convert the input value to lowercase for case-insensitive matching
        value = str(value).lower()
        for member in cls:
            if member.value.lower() == value:
                return member
        # If no match found, raise a ValueError as default behavior
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")


class Decoder(str, Enum):
    """
    Enum representing different decoders to be used for QEC experiment.
    """

    PYMATCHING = "pymatching"
    BELIEFPROPAGATION = "beliefpropagation"
    UNIONFIND = "unionfind"
    LUT = "lut"

    @classmethod
    def _missing_(cls, value):
        # Convert the input value to lowercase for case-insensitive matching
        value = str(value).lower()
        for member in cls:
            if member.value.lower() == value:
                return member
        # If no match found, raise a ValueError as default behavior
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")


class NoiseParameters(StrictBaseModel):
    """
    Enum representing different noise models that can be used in
    quantum error correction experiments.
    """

    depolarizing: float = Field(
        default=0, validate_default=True, description="Depolarizing error rate"
    )
    measurement: float = Field(
        default=0, validate_default=True, description="Measurement error rate"
    )
    reset: float = Field(
        default=0, validate_default=True, description="Reset error rate"
    )


class QECExperiment(StrictBaseModel):
    """
    Parameters for a quantum error correction experiment.
    This includes the code type, distance, number of rounds,
    decoder to be used, and noise model.
    """

    qec_code: Code
    decoder: Decoder
    noise_parameters: NoiseParameters | list[NoiseParameters] = Field(
        default_factory=list,
        description="Parameters for the noise model used in the experiment",
    )
    max_shots: int = Field(
        default=1000000,
        description="Number of shots for the simulation of the quantum error correction experiment",
    )
    max_errors: int = Field(
        default=500,
        description="Maximum number of errors detected before the simulation is stopped",
    )
    gate_durations: dict[str, float] | None = Field(
        default=None,
        description="Duration of quantum gates used in the experiment",
        validate_default=True,
    )
    experiment_type: str = Field(
        description="Type of the experiment, e.g., memory",
    )
    pseudoseed: int = Field(
        default_factory=lambda _: randint(0, 2**32 - 1),
        description="Pseudorandom seed for the experiment. Randomized by default.",
    )

    def model_post_init(self, __context) -> None:
        """
        Post-initialization that recasts noise_parameters to a list if it is a single instance.
        """
        self.noise_parameters = (
            [self.noise_parameters]
            if isinstance(self.noise_parameters, NoiseParameters)
            else self.noise_parameters
        )


class QECExperimentXZ(QECExperiment):
    """
    Parameters for a quantum error correction experiment with both X and Z memory types.
    Inherits from QECExperiment and can be extended with additional parameters if needed.
    """

    memory_type: str = Field(
        description="Type of memory used in the experiment, either 'Z' or 'X'",
    )

    @field_validator("memory_type", mode="before")
    @classmethod
    def validate_memory_type(cls, v: str) -> str:
        """
        Validate the memory_type field to ensure it is either 'Z' or 'X'.
        This is case-insensitive, so both 'Z' and 'z' are valid.
        """
        v = str(v).strip()
        if v.upper() not in {"Z", "X"}:
            raise ValueError("memory_type must be either 'Z' or 'X' (case-insensitive)")
        return v.upper()  # Normalize to uppercase if needed


class QECExperimentIndividual(QECExperimentXZ):
    """
    Parameters for a single instance of the Memory experiment with a single distance,
    number of rounds and a single set of noise parameters.
    Inherits from QECExperimentXZ and can be extended with additional parameters if needed.
    """

    distance: int = Field(
        description="The distance of the code all individual experiments will run for",
    )
    num_round: int = Field(
        description="The number of syndrome extraction rounds for the distance",
    )
    experiment_type: str = "individual"

    @field_validator("noise_parameters", mode="before")
    @classmethod
    def validate_noise_parameters(
        cls, v: NoiseParameters | list[NoiseParameters]
    ) -> NoiseParameters:
        """
        Validate the noise_parameters field to ensure that there is only 1 NoiseParameter.
        """
        if isinstance(v, NoiseParameters):
            return v
        if isinstance(v, list) and len(v) == 1 and isinstance(v[0], NoiseParameters):
            return v[0]
        raise ValueError(
            "noise_parameters must be a single NoiseParameters instance or a list with exactly one NoiseParameters instance"
        )

    def model_dump(self, *args, **kwargs):
        """
        Override model_dump to ensure distance and num_rounds get recasted to lists.
        """
        data = super().model_dump(*args, **kwargs)
        data["distance_range"] = [data["distance"]]
        data["num_rounds"] = [data["num_round"]]
        data.pop("distance", None)
        data.pop("num_round", None)
        return data


class MemoryExperiment(QECExperimentXZ):
    """
    Parameters for a quantum error correction memory experiment.
    Inherits from QECExperiment and can be extended with additional parameters if needed.
    """

    distance: int = Field(
        description="The distance of the code all memory experiments will run for",
    )
    num_rounds: list[int] = Field(
        description="The varying number of syndrome extraction rounds for the distance",
    )
    experiment_type: str = "memory"

    def model_dump(self, *args, **kwargs):
        """
        Override model_dump to ensure distance and num_rounds get recasted to lists.
        """
        data = super().model_dump(*args, **kwargs)
        data["distance_range"] = [data["distance"]] * len(data["num_rounds"])
        data.pop("distance", None)
        return data


class ThresholdExperiment(QECExperimentXZ):
    """
    Parameters for a quantum error correction threshold experiment.
    Inherits from QECExperiment and can be extended with additional parameters if needed.
    """

    # All pairs of distance_range and num_rounds will be run for each noise rate.
    distance_range: list[int] = Field(
        description="The various distances the threshold experiment will run for",
    )
    num_rounds: list[int] = Field(
        description="The number of syndrome extraction rounds for each distance in distance_range",
    )
    experiment_type: str = "threshold"

    @model_validator(mode="after")
    @classmethod
    def validate_num_rounds_distance_range_length(cls, values):
        """
        Validate the num_rounds and distance_range fields to ensure they have the same length.
        """
        if len(values.num_rounds) != len(values.distance_range):
            raise ValueError("num_rounds must have the same length as distance_range")
        return values


class QECResult(StrictBaseModel):
    """
    Result of a quantum error correction experiment.
    """

    timestamp: str = Field(
        description="Timestamp when the experiment was executed",
    )
    noise_parameters: NoiseParameters | list[NoiseParameters] = Field(
        description="Parameters for the noise model used in the experiment",
    )
    logical_error_rate: list[list[float]] = Field(
        description="Logical error rate of the quantum error correction experiment",
    )
    raw_results: dict = Field(
        description="Raw results of the quantum error correction experiment",
    )
    code_threshold: float | None = Field(
        default=None,
        description="Computed threshold for the quantum error correction "
        "code used in the experiment",
    )

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create an instance of QECResult from a dictionary.
        This is useful for deserializing results from JSON or other formats.
        """
        # Select result
        data = data["result"]
        # Format the noise_parameters field based on its length
        if len(data["noise_parameters"]) > 1:
            output_noise_parameters = [
                NoiseParameters(**np) for np in data["noise_parameters"]
            ]
        else:
            output_noise_parameters = NoiseParameters(**data["noise_parameters"][0])

        return cls(
            timestamp=data["timestamp"],
            noise_parameters=output_noise_parameters,
            logical_error_rate=data["logical_error_rate"],
            code_threshold=data["threshold"],
            raw_results=data,
        )

    @property
    def results_overview(self) -> dict:
        """
        Returns a summary of the results sorted by noise parameters:
        - Each noise parameter will have a list of dictionaries for the various
          combinations of distance, num_rounds runs and their respective
          logical_error_rate.
        - This is useful for quickly accessing the results of the experiment.

        Example output:
        {
            "timestamp": "2023-10-01T12:00:00Z",
            "results": [
                {
                    "noise_parameters": NoiseParameters(depolarizing=0.01, measurement=0.01, reset=0.01),
                    "runs": [
                        {
                            "distance": 3,
                            "num_rounds": 5,
                            "logical_error_rate": 0.001
                        },
                        {
                            "distance": 5,
                            "num_rounds": 10,
                            "logical_error_rate": 0.002
                        }
                    ]
                },
                ...
            ],
            "code_threshold": 0.1
        }
        """
        temp_noise_parameters = (
            [self.noise_parameters]
            if isinstance(self.noise_parameters, NoiseParameters)
            else self.noise_parameters
        )
        formatted_results = []

        for i, noise_parameters in enumerate(temp_noise_parameters):
            formatted_results.append({"noise_parameters": noise_parameters, "runs": []})
            for j, (distance, num_rounds) in enumerate(
                zip(self.raw_results["distance_range"], self.raw_results["num_rounds"])
            ):
                formatted_results[i]["runs"].append(
                    {
                        "distance": distance,
                        "num_rounds": num_rounds,
                        "logical_error_rate": self.logical_error_rate[i][j],
                    }
                )

        return {
            "timestamp": self.timestamp,
            "experiment_type": self.raw_results["experiment_type"],
            "results": formatted_results,
            "code_threshold": self.code_threshold,
        }
