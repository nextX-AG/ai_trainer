import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const porndbApi = {
    searchVideos: async (projectId: string, keyword: string) => {
        const response = await axios.post(`${API_BASE_URL}/projects/${projectId}/search`, {
            keyword
        });
        return response.data;
    },

    downloadVideo: async (projectId: string, videoId: string) => {
        const response = await axios.post(`${API_BASE_URL}/projects/${projectId}/download`, {
            videoId
        });
        return response.data;
    },

    getDownloadProgress: async (projectId: string, downloadId: string) => {
        const response = await axios.get(
            `${API_BASE_URL}/projects/${projectId}/download/${downloadId}/progress`
        );
        return response.data;
    }
}; 