import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TwophasesComponent } from './twophases.component';

describe('TwophasesComponent', () => {
  let component: TwophasesComponent;
  let fixture: ComponentFixture<TwophasesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TwophasesComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TwophasesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
