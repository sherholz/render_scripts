test_case_description = "This is an example description of the test case"


common_params = {"__INTEGRATOR__": "volpath",
                 "sampleCount": 32,
                 "maxDepth": 8,
                 "rrDepth": 8,
                 }

test_cases = {
    "vol": {"param": {"__INTEGRATOR__": "volpath",
                      "sampleCount": 32,
                      },
            "description": "Standard Volumetric Path Tracer",
            },
    "bdpt": {"param": {"__INTEGRATOR__": "bdpt",
                       "sampleCount": 32,
                       },
             "description": "Bi-directional Volumetric Path Tracer",
             },
}
