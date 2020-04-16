import { configureStore } from '@reduxjs/toolkit';
import counterReducer from '../features/counter/counterSlice';
import gallerySlice from '../features/gallery/gallerySlice';

export default configureStore({
  reducer: {
    gallerySlice: gallerySlice,
  },
});
