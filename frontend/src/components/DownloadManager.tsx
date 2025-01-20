import React from 'react';
import { 
    Card, 
    List, 
    ListItem, 
    ListItemText,
    LinearProgress,
    Typography
} from '@mui/material';
import { useQuery } from 'react-query';
import { porndbApi } from '../api/porndb';

interface DownloadManagerProps {
    projectId: string;
    downloads: Array<{
        id: string;
        name: string;
        status: 'pending' | 'downloading' | 'completed' | 'error';
    }>;
}

export const DownloadManager: React.FC<DownloadManagerProps> = ({ 
    projectId, 
    downloads 
}) => {
    return (
        <Card sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
                Downloads
            </Typography>
            <List>
                {downloads.map((download) => (
                    <ListItem key={download.id}>
                        <ListItemText 
                            primary={download.name}
                            secondary={download.status}
                        />
                        {download.status === 'downloading' && (
                            <LinearProgress 
                                sx={{ width: '100%', ml: 2 }} 
                                variant="determinate" 
                                value={75} 
                            />
                        )}
                    </ListItem>
                ))}
            </List>
        </Card>
    );
}; 