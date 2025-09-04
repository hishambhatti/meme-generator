import Caption from "./Caption";
import FileDrop from "./FileDrop";
import Button from "./component/Button";
import { useState, useRef } from "react";

function App() {
  const [imgpath, setImgpath] = useState("");
  const [caption, setCaption] = useState("");

  const imgRef = useRef(new FormData());

  const backendUrl = "https://meme-generator-ai-backend-451189649542.us-west1.run.app"

  let retryImage: React.MouseEventHandler<HTMLButtonElement> = () => {
    setImgpath("");
    setCaption("");
  };

  let generateCaption = () => {
    console.log("TEST!!")
    // make two requests to backend,

    // upload the image to the backend using /upload-img
    fetch(backendUrl + "/upload-img", {
      method: "POST",
      body: imgRef.current,
      headers: {
        "Access-Control-Allow-Origin": "*",
      },
    }).then(async (response) => {
      if (!response.ok) {
        throw new Error("upload to backend failed");
      }

      let x = await response.json();

      let response2 = await fetch(
        backendUrl + "/cap-generate?src=" + x.filename,
        {
          headers: { "Access-Control-Allow-Origin": "*" },
        }
      );

      setCaption((await response2.json()).caption);
    });
  };

  let onChangeHandler: React.ChangeEventHandler<HTMLInputElement> = (event) => {
    const file = event.target.files?.[0];

    if (file) {
      // Create a URL for the selected file
      const reader = new FileReader();

      // store the image (so that when we request the backend, we have something
      // to give)
      const formData = new FormData();
      formData.append("image_file", file);

      imgRef.current = formData;

      reader.onloadend = () => {
        setImgpath(reader.result as string);
      };
      reader.readAsDataURL(file);
    } else {
      setImgpath("");
    }
  };

  // function to draw the image to canvas
  function draw(
    canvas: HTMLCanvasElement,
    ctx: CanvasRenderingContext2D,
    downloadLink: HTMLAnchorElement
  ) {
    if (ctx == null) {
      return;
    }

    let img = new Image();
    img.src = imgpath;
    img.onload = () => {
      canvas.width = 720;
      canvas.height = 720;
      ctx.fillStyle = "white";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // img height after scaling so that the width matches the screen
      const scaledImgHeight = (canvas.width / img.width) * img.height;

      // offset for leaving space for the caption at the top
      const captionoffset = 75;

      // padding to leave a bit of space at the bottom
      const bottomPadding = 25;

      // maximum image height before it starts getting cropped by the canvas
      const maxImgHeight = canvas.height - captionoffset - bottomPadding;

      // check if scaling width to canvas causes cropping
      if (scaledImgHeight <= maxImgHeight) {
        // scale to width was ok
        canvas.height = scaledImgHeight + captionoffset + bottomPadding;
        ctx.drawImage(img, 0, captionoffset, canvas.width, scaledImgHeight);
      } else {
        console.log("here");
        // scale to width failed, scale to height instead
        const scaledImgWidth = (maxImgHeight / img.height) * img.width;
        ctx.drawImage(
          img,
          (canvas.width - scaledImgWidth) / 2,
          captionoffset,
          scaledImgWidth,
          maxImgHeight
        );
      }

      // figure out how many lines it will take
      ctx.fillStyle = "black";
      ctx.font = "24px sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";

      let words = caption.split(" ");
      let currLine = "";
      let lines = [];

      for (let i = 0; i < words.length; i++) {
        let lineBeforeAdd = currLine;
        currLine = currLine + words[i] + " ";
        let lineLength = ctx.measureText(currLine);

        if (lineLength.width > canvas.width && i > 0) {
          lines.push(lineBeforeAdd);
          currLine = words[i] + " ";
        }
      }
      lines.push(currLine);

      console.log(lines);

      if (lines.length == 2) {
        ctx.fillText(lines[0], canvas.width / 2, captionoffset / 4);
        ctx.fillText(lines[1], canvas.width / 2, (3 * captionoffset) / 4);
      } else {
        ctx.fillText(lines[0], canvas.width / 2, captionoffset / 2);
      }

      const dataURL = canvas.toDataURL();
      downloadLink.href = dataURL;
      downloadLink.click();
    };
  }

  function onDownloadPress() {
    // draw the desired image to the canvas
    const canvas = document.getElementById("canvas") as HTMLCanvasElement;
    const ctx = canvas.getContext("2d") as CanvasRenderingContext2D;
    const downloadLink = document.getElementById(
      "downloadLink"
    ) as HTMLAnchorElement;

    draw(canvas, ctx, downloadLink);

    // save the image to the user's downloads
  }

  return (
    <>
      <div className="flex flex-col grow items-center h-full pl-10 pr-10 mb-3">
        <h1 className="pt-10 font-light text-slate-800 text-5xl md:text-6xl lg:text-8xl text-center">
          Live, Laugh, Learn
        </h1>
        <h3 className="p-3 text-xl md:text-2xl lg:text-3xl font-light text-slate-800 text-center">
          A deep learning model for humorous image captioning.
        </h3>
        {imgpath == "" ? (
          <FileDrop onChangeEvent={onChangeHandler}>
            Select an image (.png, .jpg, .jpeg, or .heic) to be meme-ified!
          </FileDrop>
        ) : undefined}

        {imgpath == "" ? undefined : (
          <img src={imgpath} className="max-h-128"></img>
        )}

        <Caption text={caption == "" ? undefined : caption} />

        {caption != "" || imgpath == "" ? undefined : (
          <Button
            className="max-w-xl w-full bg-blue-500"
            onClick={generateCaption}
          >
            Generate Meme
          </Button>
        )}

        {caption == "" ? undefined : (
          <Button
            onClick={onDownloadPress}
            className="max-w-lg w-full bg-emerald-400"
          >
            Download Meme <i className="fa-solid fa-file-arrow-down"></i>
          </Button>
        )}
        {caption == "" ? undefined : (
          <Button className="max-w-xl w-full bg-blue-500" onClick={retryImage}>
            Try Another Image
          </Button>
        )}

        {/* These hidden elements are used for the download functionality */}
        <canvas
          className="hidden"
          id="canvas"
          width="720"
          height="720"
        ></canvas>
        <a id="downloadLink" className="hidden" download></a>
      </div>
    </>
  );
}

export default App;
