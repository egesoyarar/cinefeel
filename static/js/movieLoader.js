import API from './api.js';
import { debounce } from './utils.js';

class MovieLoader {
    constructor() {
        this.currentPage = 1;
        this.isLoading = false;
        this.hasMore = true;
        this.init();
    }

    async loadMovies() {
        if (this.isLoading || !this.hasMore) return;
        
        try {
            this.isLoading = true;
            this.showLoader();
            
            const data = await API.getMovies(this.currentPage);
            this.renderMovies(data.movies);
            this.hasMore = data.hasMore;
            this.currentPage++;
        } catch (error) {
            console.error('Error loading movies:', error);
        } finally {
            this.isLoading = false;
            this.hideLoader();
        }
    }

    // ... rest of the movie loader implementation
}

export default MovieLoader; 