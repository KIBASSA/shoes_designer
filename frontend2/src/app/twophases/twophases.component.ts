import { Component, OnInit } from '@angular/core';
import { PaintApiService } from '../_services/paint.api.service'
@Component({
  selector: 'app-twophases',
  templateUrl: './twophases.component.html',
  styleUrls: ['./twophases.component.css']
})
export class TwophasesComponent implements OnInit {
  public imagePath;
  imgURL: any;
  imgEdgeURL : any;
  imgIBlackLeather: any;
  public message: string;

  constructor(private paintApi : PaintApiService) {}

  ngOnInit(): void {}
  fileChange(files:any) {
      if (files.length === 0)
        return;
  
      var mimeType = files[0].type;
      if (mimeType.match(/image\/*/) == null) {
        this.message = "Only images are supported.";
        return;
      }
  
      var reader = new FileReader();
      this.imagePath = files;
      reader.readAsDataURL(files[0]); 
      reader.onload = (_event) => { 
        this.imgURL = reader.result;
        console.log(this.imgURL)
      }
   }

   convertImageToEdge()
   {
     this.paintApi.generate_images(this.imgURL).subscribe(res=> 
      {
        this.imgEdgeURL = res["hed"]
        this.imgIBlackLeather = res["generated"]
      })
   }

   convertEdgeToImage()
   {
    this.paintApi.generate_shoe_by_hed(this.imgEdgeURL).subscribe(res=> 
      {
        this.imgIBlackLeather = res
      })
   }
   downloadHed()
   {
      let byteCharacters = atob(this.imgEdgeURL);

      let byteNumbers = new Array(byteCharacters.length);
      for (var i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
      }

      let byteArray = new Uint8Array(byteNumbers);

      let blob = new Blob([byteArray], {"type": "image/jpeg"});

      if(navigator.msSaveBlob){
          let filename = 'picture';
          navigator.msSaveBlob(blob, filename);
      } else {
          let link = document.createElement("a");

          link.href = URL.createObjectURL(blob);

          link.setAttribute('visibility','hidden');
          link.download = 'picture';

          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
      }
   }
   downloadGenerated()
   {

   }
}
