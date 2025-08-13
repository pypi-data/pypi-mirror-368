"""
A registry of building blocks from the control-arena library.

This can be used to map configuration values (e.g., from a YAML file)
to the actual Python classes and functions for running experiments.

This version uses importlib for lazy-loading to improve startup performance.
"""

import importlib
from typing import Any

# A cache to store the resolved/imported objects to avoid re-importing.
_resolved_cache: dict[str, Any] = {}


def _import_from_string(import_str: str) -> Any:
    """
    Imports an object from a module string.

    For example, `_import_from_string("my_package.my_module:MyClass")`
    will return the `MyClass` object from `my_package.my_module`.

    Args:
        import_str: The string representation of the object to import.

    Returns:
        The imported object.

    Raises:
        ImportError: If the module or object cannot be imported.
    """
    try:
        module_path, class_name = import_str.rsplit(":", 1)
    except ValueError as e:
        raise ImportError(f"'{import_str}' is not a valid import string.") from e

    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        raise ImportError(f"Could not import module '{module_path}'.") from e

    try:
        return getattr(module, class_name)
    except AttributeError as e:
        raise ImportError(
            f"Could not find '{class_name}' in module '{module_path}'."
        ) from e


# ============================================================================
# Registry Definition
# ============================================================================
# Instead of direct imports, we store the full import path as a string.
# The format is "path.to.module:ObjectName".
# The `resolve_type` function will handle the dynamic import.
# ============================================================================

BUILDING_BLOCKS = {
    "settings": {
        "agentdojo": "control_arena.settings.agentdojo_setting.agentdojo_setting:AgentDojoSetting",
        "apps": "control_arena.settings.apps.apps_setting:AppsSetting",
        "bash": "control_arena.settings.bash.bash_setting:BashSetting",
        "data_poisoning": "control_arena.settings.data_poisoning.data_poisoning_setting:DataPoisoningSetting",
        "eval_sabotage": "control_arena.settings.eval_sabotage.setting:EvalSabotageSetting",
        "iac": "control_arena.settings.iac.control_iac_setting:ControlIACSetting",
        "infra": "control_arena.settings.infra.infra_setting:InfraSetting",
        "rogue_eval": "control_arena.settings.rogue_eval.rogue_eval_setting:RogueEvalSetting",
        "sae_interp_sabotage": "control_arena.settings.sae_interp_sabotage.setting:SAEInterpSetting",
        "shade_arena": "control_arena.settings.shade_arena.shade_arena_setting:ShadeArenaSetting",
        "vllm": "control_arena.settings.vllm.vllm_setting:VLLMSetting",
    },
    "policies": {
        # Core policies
        "attack_policy": "control_arena.policy.attack_policy:attack_policy",
        "AttackPolicyFromFile": "control_arena.policy.attack_policy_from_file:attack_policy_from_file",
        "fixed_policy": "control_arena.policy.fixed_policy:fixed_policy",
        "honest_policy": "control_arena.policy.honest_policy:honest_policy",
        "untrusted_policy": "control_arena.policy.untrusted_policy:untrusted_policy",
        # Setting-specific policies
        "agentdojo_defense": "control_arena.settings.agentdojo_setting.policy:agentdojo_defense",
        "agentdojo_fixed": "control_arena.settings.agentdojo_setting.policy:agentdojo_fixed",
        "apps_backdoor_attack_policy": "control_arena.settings.apps.apps_backdoor_attack_policy:apps_backdoor_attack_policy",
        "known_strings_attack_policy": "control_arena.settings.bash.policies.known_strings:known_strings_attack_policy",
        "qa_honest_policy": "control_arena.settings.infra.policies.qa_policies:qa_honest_policy",
        "qa_attack_policy": "control_arena.settings.infra.policies.qa_policies:qa_attack_policy",
        "replay_model_attacks_policy": "control_arena.settings.infra.policies.replay_model_attacks:replay_model_attacks_policy",
    },
    "monitors": {
        "basic_monitor": "control_arena.monitor.basic_monitor:basic_monitor",
        "cot_monitor": "control_arena.monitor.cot_monitor:cot_monitor",
        "cot_only_monitor": "control_arena.monitor.cot_only_monitor:cot_only_monitor",
        "diff_monitor": "control_arena.monitor.diff_monitor:diff_monitor",
        "ensemble_monitor": "control_arena.monitor.ensemble_monitor:ensemble_monitor",
        "prefix_monitor": "control_arena.monitor.prefix_monitor:prefix_monitor",
    },
    "protocols": {
        "dtr_protocol": "control_arena.protocol.dtr_protocol:dtr_protocol",
        "dtt_protocol": "control_arena.protocol.dtt_protocol:dtt_protocol",
        "dtte_protocol": "control_arena.protocol.te_protocol:dtte_protocol",
        "tm_protocol": "control_arena.protocol.tm_protocol:tm_protocol",
    },
    "scorers": {
        # Core scorers
        "blabbing_scorer": "control_arena.scorers.blabbing_scorer:blabbing_scorer",
        "combined_pr_scorer": "control_arena.scorers.llm_judge:combined_pr_scorer",
        # Suspicion (monitoring) scorers
        "git_diff_monitor": "control_arena.suspicion_scorers.diff_monitor:git_diff_monitor",
        "full_trajectory_monitor": "control_arena.suspicion_scorers.full_trajectory_monitor:full_trajectory_monitor",
        "finegrained_trajectory_monitor": "control_arena.suspicion_scorers.full_trajectory_monitor:finegrained_trajectory_monitor",
        "no_reasoning_trajectory_monitor": "control_arena.suspicion_scorers.full_trajectory_monitor:no_reasoning_trajectory_monitor",
        "control_monitor": "control_arena.suspicion_scorers.full_trajectory_monitor:control_monitor",
        "task_drift_monitor": "control_arena.suspicion_scorers.full_trajectory_monitor:task_drift_monitor",
        "no_reasoning_task_drift_monitor": "control_arena.suspicion_scorers.full_trajectory_monitor:no_reasoning_task_drift_monitor",
        "ensemble_full_trajectory_monitor": "control_arena.suspicion_scorers.full_trajectory_monitor:ensemble_full_trajectory_monitor",
        "ensemble_no_reasoning_trajectory_monitor": "control_arena.suspicion_scorers.full_trajectory_monitor:ensemble_no_reasoning_trajectory_monitor",
        "ensemble_task_drift_monitor": "control_arena.suspicion_scorers.full_trajectory_monitor:ensemble_task_drift_monitor",
        "diverse_ensemble_monitor": "control_arena.suspicion_scorers.full_trajectory_monitor:diverse_ensemble_monitor",
        "max_suspicion_scorer": "control_arena.suspicion_scorers.max:max_suspicion_scorer",
        # Setting-specific scorers
        "agentdojo_scorer": "control_arena.settings.agentdojo_setting.scorer:agentdojo_scorer",
        "apps_scorer": "control_arena.settings.apps.task.scorers:apps_scorer",
        "bash_scorer": "control_arena.settings.bash.task.scorers:bash_scorer",
        "data_poisoning_scorer": "control_arena.settings.data_poisoning.scorers:data_poisoning_scorer",
        "combined_pytest_scorer": "control_arena.settings.iac.scorers:combined_pytest_scorer",
        "k8s_scorer": "control_arena.settings.infra.task.scorer:k8s_scorer",
        "rogue_eval_scorer": "control_arena.settings.rogue_eval.scorer:rogue_eval_scorer",
        "sae_interp_scorer": "control_arena.settings.sae_interp_sabotage.scorers:sae_interp_scorer",
        "shade_arena_scorer": "control_arena.settings.shade_arena.scorer:shade_arena_scorer",
        "vllm_scorer": "control_arena.settings.vllm.task.scorers:vllm_scorer",
    },
    "tools": {
        "restricted_bash": "control_arena.tools.restricted_bash:restricted_bash",
        "restricted_bash_session": "control_arena.tools.restricted_bash:restricted_bash_session",
        "restricted_text_editor": "control_arena.tools.restricted_text_editor:restricted_text_editor",
        "bash_run_tests": "control_arena.settings.bash.task.tools:run_tests",
        "cdk_ls": "control_arena.settings.iac.tools:cdk_ls",
        "build_dockerfiles": "control_arena.settings.infra.tools:build_dockerfiles",
        "upload_code": "control_arena.settings.rogue_eval.tools:upload_code",
        "rogue_eval_submit": "control_arena.settings.rogue_eval.tools:submit",
    },
}


def resolve_type(type_name: str) -> Any:
    """
    Look for type_name in all namespaces of BUILDING_BLOCKS, import it,
    and return the actual object.

    This function caches results, so subsequent calls for the same
    type_name are fast.

    Args:
        type_name: The name of the component to resolve (e.g., "honest_policy").

    Returns:
        The imported class or function corresponding to type_name.

    Raises:
        KeyError: If the component type is not found in the registry.
        ImportError: If the component fails to import.
    """
    # Check cache first for fast lookups
    if type_name in _resolved_cache:
        return _resolved_cache[type_name]

    # Find the import string in our registry
    for namespace in BUILDING_BLOCKS.values():
        if type_name in namespace:
            import_str = namespace[type_name]
            resolved_object = _import_from_string(import_str)
            # Cache the successfully imported object before returning
            _resolved_cache[type_name] = resolved_object
            return resolved_object

    raise KeyError(f"Component type '{type_name}' not found in registry.")
