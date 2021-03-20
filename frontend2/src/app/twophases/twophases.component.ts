import { Component, OnInit,TemplateRef, ViewChild } from '@angular/core';
import { PaintApiService } from '../_services/paint.api.service'
import { NgbModal,NgbModalRef } from '@ng-bootstrap/ng-bootstrap';
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
  loading:boolean
  modalReference: NgbModalRef;
  @ViewChild('chooseImageModal', {static: false}) chooseImageModal : TemplateRef<any>; // Note: TemplateRef
  constructor(private paintApi : PaintApiService,
    private modalService: NgbModal) {}

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
        this.imgEdgeURL = null
        this.imgIBlackLeather = null
        console.log(this.imgURL)
      }
   }

   convertImageToEdge()
   {
     this.loading = true
     this.paintApi.generate_images_post(this.imgURL).subscribe(res=> 
      {
        this.imgEdgeURL = res["hed"]
        this.imgIBlackLeather = res["generated"]
        this.loading = false
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
   chooseImage()
   {
    this.modalReference = this.modalService.open(this.chooseImageModal, { size: 'lg'});
   }
  
   getImagesList()
   {
      var images = []
      Array.from(Array(148).keys()).forEach(a=> 
      {
        images.push("assets/shoes/" + a.toString() + ".jpg")
      });
     return images
   }
   ImageChoosed(image:any)
   {
    console.log(image)
    this.paintApi.getBase64ImageFromURL(image).subscribe(res=> 
      {
        console.log(res)
        var reader = new FileReader();
        reader.readAsDataURL(res); 
        reader.onload = (_event) => { 
        this.imgURL = reader.result;
        this.modalReference.close();
        }
      })
   }
   
   downloadGenerated()
   {

   }
}
