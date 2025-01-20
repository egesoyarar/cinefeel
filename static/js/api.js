const API = {
    async getMovies(page) {
        const response = await fetch(`/api/movies?page=${page}`);
        return response.json();
    }
};

export default API; 