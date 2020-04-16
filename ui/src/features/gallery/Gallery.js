import styles from '../styles.css';


import React, { Component } from 'react'
import { connect } from 'react-redux';
import { fetchDefaultAlbum } from './galleryActions';
import { changeViewTimeout } from './gallerySlice';

import backgrpundImage from '../backgrpundImage.jpg';
import backgrpundImage2 from '../backgroundImage2.jpg';

import FullScreen from 'react-full-screen';

import CONSTANTS from '../constants';
import store from '../../app/store';
import ServerConnect from '../ServerConnect';


class Gallery extends Component {

    constructor(props) {
        super(props)
        this.startButtonRef = React.createRef();
        this.state = {
            isFull: false,
            currentImage: backgrpundImage,
            paused: false,
            stopped: false,
            timerID: 0,
            slideTimeout: 1000,
            autoStart: true,
            currentIndex: 0
        }
    }

    componentDidMount() {
        this.props.fetchDefaultAlbum();
    }

    handleFullScreenRequest = () => {
        window.document.querySelector('.gallery').requestFullscreen();

        this._loopSlide();
    }

    stopSlide = (callback) => {
        clearInterval(this.state.timerID);
        console.log("stopped  " + this.state.timerID);
        this.setState({
            timerID: "",
            stopped: true,
        }, () => callback())
    };

    pauseSlide = () => {
        this.setState({
            paused: true,
            stopped: this.state.stopped ? false : true
        });
    }

    _detectNextIndex = (defaultAlbumImages) => {
        return this.state.currentIndex + 1 < defaultAlbumImages.length ?
            this.state.currentIndex + 1 : 0;
    }

    _changeGalleryView = () => {
        const defaultAlbumImages = this.props.defaultAlbum.images;
        const nextIndex = this._detectNextIndex(defaultAlbumImages);
        this.setState({
            currentIndex: nextIndex,
            currentImage: CONSTANTS.SERVER_URL + defaultAlbumImages[nextIndex].imageFile
            // currentImage: this.state.currentImage == backgrpundImage ? backgrpundImage2 : backgrpundImage
        });
    }

    _loopSlide = (newSeconds = this.state.slideTimeout) => {
        console.log(this.state.paused + " " + this.state.stopped);

        if (this.state.paused && !this.state.stopped) {
            this.playSlide();
            console.log("Gallery already being played..");
            return;
        }

        // This method can only start a timer if the gallery has been paused.
        // It can only stop or pause playing the gallery if the pause or stopped has bee
        // set to true

        if (this.state.stopped && this.state.timerID == "") {
            this.state['stopped'] = false;
            this.state['timerID'] = setInterval(() => {
                if (!this.state.paused && !this.state.stopped) {
                    console.log("Still paying");
                    this._changeGalleryView();
                } else {
                    console.log("Gallery Paused");
                    return;
                }
            }, newSeconds);
            console.log("started" + this.state.timerID + ` in these conditions paused? ${this.state.paused} and timerID ${this.state.timerID} and seconds ` + newSeconds);

        } else {
            console.log("Can not play");
        }
    }

    playSlide = () => {
        console.log("Paused before playing " + this.state.paused + " stopped => " + this.state.stopped);
        this.setState({
            // check the paused state to decide on what to do,
            // this can be either the server sent soemthing and we need to restart
            stopped: this.state.paused == false && this.state.stopped ? false : true,
            paused: false,
        }, () => this._loopSlide());
    }

    changeTimeout = (newSeconds) => {
        // console.log("newSeconds " + newSeconds);
        this.stopSlide(() =>
            this.setState({
                paused: false,
                slideTimeout: newSeconds
            }, () => this._loopSlide(newSeconds)));
    }

    handlePause = () => {
        if (this.state.paused) {
            this.playSlide();
        } else {
            this.pauseSlide();
        }
    }

    decreaseSpeed = () => {
        if ((this.state.slideTimeout - 1000) > 0) {
            this.changeTimeout(this.state.slideTimeout - 1000);
        }
    }

    inCreaseSpeed = () => {
        this.changeTimeout(this.state.slideTimeout + 1000);
    }

    render() {
        this.state['slideTimeout'] = this.props.viewTimeout;
        // Start playing the image
        setTimeout(() => {
            if (this.state.autoStart) {
                this.state['autoStart'] = false;
                this.startButtonRef.current.click();
            }
        }, 1000);

        return (

            <div className="gallery-box" >
                <div className="gallery-controls" >
                    <button className="hide" onClick={() => this.playSlide()} ref={this.startButtonRef} >Start</button>
                    <button className="button button-primary pause-button" onClick={() => this.decreaseSpeed()} >- Speed</button>
                    <button className="button button-primary fulscreen-button" onClick={() => this.handleFullScreenRequest()} >Go Full Screen</button>
                    <button className="button button-primary pause-button" onClick={() => this.handlePause()} > {this.state.paused ? "Play" : "Pause"} </button>
                    <button className="button button-primary pause-button" onClick={() => this.inCreaseSpeed()} >+ Speed</button>
                    <label className="timer-speed" > {this.state.slideTimeout / 1000}x </label>
                </div>
                <div ref={this.galleryRef} className="container gallery" >
                    <img className="gallery-active" src={this.state.currentImage} />

                    {/* <FullScreen
                        enabled={this.state.isFull}
                        onChange={isFull => this.setState({ isFull })}>
                        <img className="gallery-active" src={this.state.currentImage} />
                    </FullScreen> */}

                </div >

                <ServerConnect
                    onMessage={this.handleReceivedSignal}
                />
                {/* <Websocket
                    url={`${CONSTANTS.WEBSOCKET_URL}`}
                    onMessage={this.handleReceivedSignal}
                /> */}
            </div >
        )
    }

    componentDidCatch(error, info) {
        console.log(error);
        console.log(info);
    }

    handleReceivedSignal = (data) => {
        console.log(data);
        let result = JSON.parse(data);
        console.log(result);
        if (result.type == "UPDATE_DEFAULT_ALBUM") {
            this.props.fetchDefaultAlbum();
        } else if (result.type == "UPDATE_GALLERY_TIMER") {
            this.changeTimeout(result.payload.new_seconds * 1000);
            store.dispatch(changeViewTimeout(result.payload.new_seconds * 1000));
        }
    }
}

const mapStateToProps = (state) => {
    console.log(state);
    return {
        defaultAlbum: state.gallerySlice.album,
        viewTimeout: state.gallerySlice.viewTimeout == 0 ? state.gallerySlice.album.viewTimeout : state.gallerySlice.viewTimeout
    }
}

export default connect(mapStateToProps, {
    fetchDefaultAlbum
})(Gallery);
