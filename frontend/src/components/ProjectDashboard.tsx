import React, { useState } from 'react';
import { Tabs, Tab, Box } from '@mui/material';
import DataAcquisition from './sections/DataAcquisition';
import VideoProcessing from './sections/VideoProcessing';
import Training from './sections/Training';
import ModelManagement from './sections/ModelManagement';

interface ProjectDashboardProps {
  projectId: string;
}

export const ProjectDashboard: React.FC<ProjectDashboardProps> = ({ projectId }) => {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <Box sx={{ width: '100%' }}>
      <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
        <Tab label="Datenerfassung" />
        <Tab label="Videoverarbeitung" />
        <Tab label="Training" />
        <Tab label="Modelle" />
      </Tabs>

      <Box sx={{ p: 3 }}>
        {activeTab === 0 && <DataAcquisition projectId={projectId} />}
        {activeTab === 1 && <VideoProcessing projectId={projectId} />}
        {activeTab === 2 && <Training projectId={projectId} />}
        {activeTab === 3 && <ModelManagement projectId={projectId} />}
      </Box>
    </Box>
  );
}; 