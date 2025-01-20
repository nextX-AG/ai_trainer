import React, { useState } from 'react';
import { 
  Card, 
  Grid, 
  TextField, 
  Button, 
  Chip,
  LinearProgress,
  Box
} from '@mui/material';
import { ImageGrid } from '../common/ImageGrid';
import { ScrapingConfig } from '../../types/scraping';

export const DataAcquisition: React.FC<{ projectId: string }> = ({ projectId }) => {
  const [keywords, setKeywords] = useState<string[]>([]);
  const [newKeyword, setNewKeyword] = useState('');
  const [scraping, setScraping] = useState(false);
  const [progress, setProgress] = useState(0);

  const startScraping = async () => {
    setScraping(true);
    // API-Aufruf zum Starten des Scrapings
    // Polling für Fortschritt
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card sx={{ p: 2 }}>
          <h3>Bildsuche</h3>
          <TextField 
            fullWidth
            label="Neues Keyword"
            value={newKeyword}
            onChange={(e) => setNewKeyword(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                setKeywords([...keywords, newKeyword]);
                setNewKeyword('');
              }
            }}
          />
          <Box sx={{ mt: 2 }}>
            {keywords.map(keyword => (
              <Chip 
                key={keyword}
                label={keyword}
                onDelete={() => setKeywords(keywords.filter(k => k !== keyword))}
                sx={{ m: 0.5 }}
              />
            ))}
          </Box>
          <Button 
            variant="contained" 
            onClick={startScraping}
            disabled={scraping || keywords.length === 0}
            sx={{ mt: 2 }}
          >
            Scraping Starten
          </Button>
          {scraping && (
            <LinearProgress 
              variant="determinate" 
              value={progress} 
              sx={{ mt: 2 }}
            />
          )}
        </Card>
      </Grid>
      
      <Grid item xs={12} md={8}>
        <ImageGrid 
          images={[]} // Gescrapte Bilder
          onSelect={() => {}}
          selectable
        />
      </Grid>
    </Grid>
  );
}; 