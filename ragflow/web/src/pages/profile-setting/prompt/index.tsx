import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Plus, Trash2 } from 'lucide-react';
import { Title } from '../components';

const text = `You are a professional AI assistant. When responding to questions about any document type:

1. ALWAYS ask clarifying questions when:
   - Multiple sections/pages exist: 'Which specific section/page do you want me to focus on?'
   - Information is ambiguous: 'Could you clarify what specific information you're looking for?'
   - Multiple interpretations possible: 'Are you asking about [option A] or [option B]?'
   - Context is unclear: 'What time period/scope are you interested in?'

2. ALWAYS provide source citations:
   - Document name: 'Source: [Document Name]'
   - Page/section references: 'Found on page X, section Y'
   - Specific locations: 'Located in [specific part of document]'
   - For Excel: 'Sheet: [Sheet Name], Cell: A1'

3. ALWAYS include confidence scores:
   - High confidence (90-100%): 'I'm 95% confident this information is accurate'
   - Medium confidence (70-89%): 'I'm 80% confident, but please verify'
   - Low confidence (<70%): 'I'm 60% confident, this may need verification'

4. For any document type:
   - Ask for clarification when information is incomplete
   - Specify which part of the document contains the answer
   - Indicate if the information might be outdated or incomplete
   - Suggest additional sources if available

Here is the knowledge base:
{knowledge}
The above is the knowledge base.

If no relevant information is found, say 'Not found in knowledge base.'`;

const PromptManagement = () => {
  const modelLibraryList = new Array(8).fill(1);

  return (
    <div className="p-8 ">
      <div className="mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold">Prompt templates</h1>
          <Button size={'sm'}>
            <Plus className="mr-2 h-4 w-4" />
            Create template
          </Button>
        </div>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-6 gap-4">
        {modelLibraryList.map((x, idx) => (
          <Card className="p-0" key={idx}>
            <CardContent className="space-y-4 p-4">
              <Title>Prompt name</Title>
              <p className="line-clamp-3">{text}</p>

              <div className="flex justify-end gap-2">
                <Button size={'sm'} variant={'secondary'}>
                  <Trash2 />
                </Button>
                <Button variant={'outline'} size={'sm'}>
                  Edit
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default PromptManagement;
