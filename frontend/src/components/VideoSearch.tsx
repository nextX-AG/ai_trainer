import React, { useState } from 'react';
import { 
    TextField, 
    Button, 
    Card, 
    Grid, 
    CircularProgress,
    Typography
} from '@mui/material';
import { useQuery, useMutation } from 'react-query';
import { porndbApi } from '../api/porndb';

interface VideoSearchProps {
    projectId: string;
}

export const VideoSearch: React.FC<VideoSearchProps> = ({ projectId }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedVideo, setSelectedVideo] = useState(null);

    const { mutate: searchVideos, isLoading } = useMutation(
        (keyword: string) => porndbApi.searchVideos(projectId, keyword)
    );

    const handleSearch = () => {
        if (searchTerm) {
            searchVideos(searchTerm);
        }
    };

    return (
        <Card sx={{ p: 2 }}>
            <Grid container spacing={2}>
                <Grid item xs={12}>
                    <TextField
                        fullWidth
                        label="Suchbegriff"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                                handleSearch();
                            }
                        }}
                    />
                </Grid>
                <Grid item xs={12}>
                    <Button 
                        variant="contained" 
                        onClick={handleSearch}
                        disabled={isLoading || !searchTerm}
                    >
                        {isLoading ? <CircularProgress size={24} /> : 'Suchen'}
                    </Button>
                </Grid>
            </Grid>
        </Card>
    );
}; 