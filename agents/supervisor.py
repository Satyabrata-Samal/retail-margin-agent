def _compress_ticket(self,memory, calculation_id, content) -> str:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"""Compress this ticket. Keep: supplier_id, 
                calculation_id, loop_count, all analyst findings, 
                all decisions made, thread summary. 
                Remove: raw SQL output, verbose reasoning.
                
                Ticket:
                {content}"""
            }]
        )
        compressed = response.content[0].text
        self.execute(
            command="create",
            path=f"/memories/active_tickets/{calculation_id}.md",
            file_text=compressed
        )
        return compressed

