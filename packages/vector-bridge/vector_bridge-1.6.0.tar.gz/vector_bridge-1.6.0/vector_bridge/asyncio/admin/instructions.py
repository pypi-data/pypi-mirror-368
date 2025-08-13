from typing import List, Optional, Union

from vector_bridge import AsyncVectorBridgeClient
from vector_bridge.schema.errors.instructions import \
    raise_for_instruction_detail
from vector_bridge.schema.helpers.enums import (AIProviders, AnthropicKey,
                                                OpenAIKey, PromptKey, VLLMKey)
from vector_bridge.schema.instruction import (AgentCreate, Instruction,
                                              InstructionCreate,
                                              PaginatedInstructions,
                                              Subordinate)


class AsyncInstructionsAdmin:
    """Async admin client for instructions management endpoints."""

    def __init__(self, client: AsyncVectorBridgeClient):
        self.client = client

    async def add_instruction(self, instruction_data: InstructionCreate, integration_name: str = None) -> Instruction:
        """
        Add new Instruction to the integration.

        Args:
            instruction_data: Instruction details
            integration_name: The name of the Integration

        Returns:
            Created instruction object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/create"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.post(
            url, headers=headers, params=params, json=instruction_data.model_dump()
        ) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
            return Instruction.model_validate(result)

    async def get_instruction_by_name(
        self, instruction_name: str, integration_name: str = None
    ) -> Optional[Instruction]:
        """
        Get the Instruction by name.

        Args:
            instruction_name: The name of the Instruction
            integration_name: The name of the Integration

        Returns:
            Instruction object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction"
        params = {
            "integration_name": integration_name,
            "instruction_name": instruction_name,
        }
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            if response.status == 404:
                return None

            result = await self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
            return Instruction.model_validate(result) if result else None

    async def get_instruction_by_id(self, instruction_id: str, integration_name: str = None) -> Optional[Instruction]:
        """
        Get the Instruction by ID.

        Args:
            instruction_id: The ID of the Instruction
            integration_name: The name of the Integration

        Returns:
            Instruction object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            if response.status == 404:
                return None

            result = await self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
            return Instruction.model_validate(result) if result else None

    async def list_instructions(
        self,
        integration_name: str = None,
        limit: int = 10,
        last_evaluated_key: Optional[str] = None,
        sort_by: str = "created_at",
    ) -> PaginatedInstructions:
        """
        List Instructions for an Integration, sorted by created_at or updated_at.

        Args:
            integration_name: The name of the Integration
            limit: The number of Instructions to retrieve
            last_evaluated_key: Pagination key for the next set of results
            sort_by: The sort field (created_at or updated_at)

        Returns:
            PaginatedInstructions with instructions and pagination info
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instructions/list"
        params = {
            "integration_name": integration_name,
            "limit": limit,
            "sort_by": sort_by,
        }
        if last_evaluated_key:
            params["last_evaluated_key"] = last_evaluated_key

        headers = self.client._get_auth_headers()

        async with self.client.session.get(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
            return PaginatedInstructions.model_validate(result)

    async def delete_instruction(self, instruction_id: str, integration_name: str = None) -> None:
        """
        Delete Instruction from the integration.

        Args:
            instruction_id: The instruction ID
            integration_name: The name of the Integration
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/delete"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.delete(url, headers=headers, params=params) as response:
            await self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)

    async def add_agent(
        self, instruction_id: str, agent_data: AgentCreate, integration_name: str = None
    ) -> Instruction:
        """
        Add new Agent to an Instruction.

        Args:
            instruction_id: The ID of the Instruction
            agent_data: Agent details to create
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/agent/add"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.put(
            url, headers=headers, params=params, json=agent_data.model_dump()
        ) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
            return Instruction.model_validate(result)

    async def remove_agent(self, instruction_id: str, agent_name: str, integration_name: str = None) -> Instruction:
        """
        Remove Agent from an Instruction.

        Args:
            instruction_id: The ID of the Instruction
            agent_name: The name of the Agent to remove
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/agent/{agent_name}/remove"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.put(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
            return Instruction.model_validate(result)

    async def add_subordinate_to_agent(
        self,
        instruction_id: str,
        agent_name: str,
        subordinate_data: Subordinate,
        integration_name: str = None,
    ) -> Instruction:
        """
        Add new Subordinate to an Agent.

        Args:
            instruction_id: The ID of the Instruction
            agent_name: The name of the Agent
            subordinate_data: Subordinate details to add
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/agent/{agent_name}/subordinate/add"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.put(
            url, headers=headers, params=params, json=subordinate_data.model_dump()
        ) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
            return Instruction.model_validate(result)

    async def update_subordinate_delegate_decision(
        self,
        instruction_id: str,
        agent_name: str,
        subordinate_name: str,
        delegation_decision: str,
        integration_name: str = None,
    ) -> Instruction:
        """
        Set delegate decision for a subordinate.

        Args:
            instruction_id: The ID of the Instruction
            agent_name: The name of the Agent
            subordinate_name: The name of the Subordinate
            delegation_decision: The decision to delegate
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/agent/{agent_name}/subordinate/{subordinate_name}/update-delegate-decision"
        params = {
            "integration_name": integration_name,
            "delegation_decision": delegation_decision,
        }
        headers = self.client._get_auth_headers()

        async with self.client.session.patch(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
            return Instruction.model_validate(result)

    async def remove_subordinate_from_agent(
        self,
        instruction_id: str,
        agent_name: str,
        subordinate_name: str,
        integration_name: str = None,
    ) -> None:
        """
        Remove Subordinate from Agent.

        Args:
            instruction_id: The ID of the Instruction
            agent_name: The name of the Agent
            subordinate_name: The name of the Subordinate Agent
            integration_name: The name of the Integration
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/agent/{agent_name}/subordinate/{subordinate_name}/remove"
        params = {"integration_name": integration_name}
        headers = self.client._get_auth_headers()

        async with self.client.session.put(url, headers=headers, params=params) as response:
            await self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)

    async def update_agents_functions(
        self,
        instruction_id: str,
        agent_name: str,
        function_names: List[str],
        integration_name: str = None,
    ) -> Instruction:
        """
        Update Agent's functions.

        Args:
            instruction_id: The ID of the Instruction
            agent_name: The name of the Agent
            function_names: The function names that agent should have access to
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/agent/{agent_name}/functions/update"
        params = {
            "integration_name": integration_name,
            "function_names": function_names,
        }
        headers = self.client._get_auth_headers()

        async with self.client.session.put(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
            return Instruction.model_validate(result)

    async def update_agents_prompt(
        self,
        instruction_id: str,
        agent_name: str,
        prompt_key: PromptKey,
        prompt_value: str,
        integration_name: str = None,
    ) -> Instruction:
        """
        Update Agent's prompt.

        Args:
            instruction_id: The ID of the Instruction
            agent_name: The name of the Agent
            prompt_key: The prompt key
            prompt_value: The prompt value
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/agent/{agent_name}/prompt/update"
        params = {"integration_name": integration_name, "prompt_key": prompt_key}
        headers = self.client._get_auth_headers()

        async with self.client.session.patch(url, headers=headers, params=params, json=prompt_value) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
            return Instruction.model_validate(result)

    async def update_agents_model(
        self,
        instruction_id: str,
        agent_name: str,
        ai_provider: AIProviders,
        model: str,
        endpoint: str = None,
        integration_name: str = None,
    ) -> Instruction:
        """
        Update Agent's model.

        Args:
            instruction_id: The ID of the Instruction
            agent_name: The name of the Agent
            ai_provider: The AI Provider for the model
            model: The model value
            endpoint: The endpoint for the model (vLLM only)
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/agent/{agent_name}/model/update"
        params = {
            "integration_name": integration_name,
            "ai_provider": ai_provider,
            "model": model,
        }
        if endpoint:
            params["endpoint"] = endpoint

        headers = self.client._get_auth_headers()

        async with self.client.session.patch(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
            return Instruction.model_validate(result)

    async def update_instruction_ai(
        self,
        instruction_id: str,
        ai_provider: AIProviders,
        ai_key: Union[OpenAIKey, AnthropicKey, VLLMKey],
        ai_value: Union[str, float, int],
        integration_name: str = None,
    ) -> Instruction:
        """
        Update Instruction AI settings.

        Args:
            instruction_id: The ID of the Instruction
            ai_provider: The AI provider
            ai_key: The AI key (OpenAI, or Anthropic)
            ai_value: The value to set
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/ai/update"
        params = {
            "integration_name": integration_name,
            "ai_provider": ai_provider,
            "ai_key": ai_key,
            "ai_value": ai_value,
        }
        headers = self.client._get_auth_headers()

        async with self.client.session.patch(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
            return Instruction.model_validate(result)

    async def update_instruction_debug(
        self, instruction_id: str, debug: bool, integration_name: str = None
    ) -> Instruction:
        """
        Update Instruction debug switch.

        Args:
            instruction_id: The ID of the Instruction
            debug: The AI interactions debug switch
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/debug/update"

        params = {"integration_name": integration_name, "debug": str(debug).lower()}
        headers = self.client._get_auth_headers()

        async with self.client.session.patch(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
            return Instruction.model_validate(result)

    async def update_instruction_max_turns(
        self, instruction_id: str, max_turns: int, integration_name: str = None
    ) -> Instruction:
        """
        Update Instruction max turns.

        Args:
            instruction_id: The ID of the Instruction
            max_turns: The maximum number of turns
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/max_turns/update"
        params = {"integration_name": integration_name, "max_turns": max_turns}
        headers = self.client._get_auth_headers()

        async with self.client.session.patch(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
            return Instruction.model_validate(result)

    async def update_instruction_default_ai_provider(
        self,
        instruction_id: str,
        ai_provider: AIProviders,
        integration_name: str = None,
    ) -> Instruction:
        """
        Update Instruction default AI provider.

        Args:
            instruction_id: The ID of the Instruction
            ai_provider: The AI provider
            integration_name: The name of the Integration

        Returns:
            Updated instruction object
        """
        await self.client._ensure_session()

        if integration_name is None:
            integration_name = self.client.integration_name

        url = f"{self.client.base_url}/v1/admin/instruction/{instruction_id}/ai/default-provider"
        params = {"integration_name": integration_name, "ai_provider": ai_provider}
        headers = self.client._get_auth_headers()

        async with self.client.session.patch(url, headers=headers, params=params) as response:
            result = await self.client._handle_response(response=response, error_callable=raise_for_instruction_detail)
            return Instruction.model_validate(result)
