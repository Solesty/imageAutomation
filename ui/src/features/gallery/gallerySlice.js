import { createSlice } from '@reduxjs/toolkit';

export const gallerySlice = createSlice({
    name: 'gallery',
    initialState: {
        album: {
            viewTimeout: 1000
        },
        albumData: [],
        mode: "wake",
        autoPlayVideo: false,
        viewTimeout: 0, // in seconds 
    },
    reducers: {
        changeGalleryMode: (state, action) => {
            state.mode = action.payload;
        },
        changeViewTimeout: (state, action) => {
            state.viewTimeout = action.payload;
        },
        changeAlbum: (state, action) => {
            state.album = action.payload;
        },
        loadAlbumData: (state, action) => {
            state.albumData = action.albumData;
        },
    }

});



export const { changeViewTimeout, changeAlbum, loadAlbumData, changeGalleryMode } = gallerySlice.actions;

// The function below is called a thunk and allows us to perform async logic. It
// can be dispatched like a regular action: `dispatch(incrementAsync(10))`. This
// will call the thunk with the `dispatch` function as the first argument. Async
// code can then be executed and other actions can be dispatched
// export const fetchDefaultAlbum = () => dispatch => {

//     setTimeout(() => {
//         dispatch(incrementByAmount(amount));
//     }, 1000);
// };


export default gallerySlice.reducer;