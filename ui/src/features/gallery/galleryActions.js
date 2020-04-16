import axios from 'axios';
import CONSTANTS from '../constants'
import { changeAlbum } from './gallerySlice';
export const fetchDefaultAlbum = () => (dispatch, getState) => {

    axios.get(`${CONSTANTS.BASE_API_URL}/album/default/public`).then((res) => {
        console.log(res.data);
        dispatch(changeAlbum(res.data));
    }).catch((err) => {
        console.log(err);
    });
}