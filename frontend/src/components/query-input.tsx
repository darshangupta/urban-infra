'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Search, Lightbulb } from 'lucide-react';

interface QueryInputProps {
  onSubmit: (query: string) => void;
  isLoading?: boolean;
}

const EXAMPLE_QUERIES = [
  "Add 200 affordable housing units near BART in Hayes Valley",
  "Make the Marina District more walkable while protecting from flooding", 
  "Increase density in Mission without displacing residents",
  "What are the tradeoffs for transit-oriented housing in Hayes Valley?",
  "How would bike infrastructure affect the Mission District community?"
];

export function QueryInput({ onSubmit, isLoading = false }: QueryInputProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSubmit(query.trim());
    }
  };

  const handleExampleClick = (exampleQuery: string) => {
    setQuery(exampleQuery);
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Search className="h-6 w-6 text-blue-600" />
          Urban Planning Analysis
        </CardTitle>
        <CardDescription>
          Ask questions about housing, development, and urban planning in San Francisco neighborhoods.
          Get comprehensive impact analysis powered by AI.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            type="text"
            placeholder="What would happen if we added affordable housing in Hayes Valley?"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1"
            disabled={isLoading}
          />
          <Button 
            type="submit" 
            disabled={!query.trim() || isLoading}
            className="px-6"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                Analyzing...
              </>
            ) : (
              <>
                <Search className="h-4 w-4 mr-2" />
                Analyze
              </>
            )}
          </Button>
        </form>

        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Lightbulb className="h-4 w-4" />
            Try these example queries:
          </div>
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_QUERIES.map((example, index) => (
              <Badge
                key={index}
                variant="secondary"
                className="cursor-pointer hover:bg-secondary/80 transition-colors px-3 py-1 text-xs"
                onClick={() => handleExampleClick(example)}
              >
                {example}
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}