Ext.ux.Mask = function(mask) {
    var config = {
        mask: mask
    };
    Ext.apply(this, config);
};

Ext.extend(Ext.ux.Mask, Object, {
    init: function(c) {
        this.LetrasL = 'abcdefghijklmnopqrstuvwxyz';
        this.LetrasU = Ext.util.Format.uppercase(this.LetrasL);
        this.Letras  = this.LetrasL + this.LetrasU;
        this.Numeros = '0123456789';
        this.Fixos  = '().-:/ +';
        this.Charset = " !\"#$%&\'()*+,-./0123456789:;<=>?@" + this.LetrasU + "[\]^_/`" + this.LetrasL + "{|}~";
        c.enableKeyEvents = true;
        c.on('keypress', function(field, evt) { return this.press(field, evt) }, this);
        c.on('changemask', function(mask) { this.mask = mask }, this);
    },

    press: function(field, evt) {
        var value = field.getValue();
        var key = evt.getKey();
        var mask = this.mask;
        var objDom = field.el.dom;

        if (field.readOnly) {
            return false;
        } else if (evt) {
            if ((objDom.selectionEnd - objDom.selectionStart) > 0) {
                return true;
            }

            var tecla = this.Charset.substr(key - 32, 1);
            if (key < 32 || key == evt.BACKSPACE) {
                return true;
            }

            if (Ext.isGecko || Ext.isGecko2 || Ext.isGecko3) {
                if ((evt.charCode == 0 && evt.keyCode == 46) || evt.isSpecialKey()) return true;
            }

            var start = objDom.selectionStart;
            var end = objDom.selectionEnd;

            var tamanho = value.length;
            if (tamanho >= mask.length) {
                evt.stopEvent();
                return false;
            }

            var pos = mask.substr(start, 1);
            while (this.Fixos.indexOf(pos) != -1) {
                value = value.slice(0, start) + pos + value.slice(start);
                start++;
                end++;
                if (start >= mask.length) {
                    evt.stopEvent();
                    return false;
                }
                pos = mask.substr(start, 1);
            }

            switch (pos) {
                case '#':
                    if (this.Numeros.indexOf(tecla) == -1) {
                        evt.stopEvent();
                        return false;
                    }
                    break;
                case 'A':
                    tecla = tecla.toUpperCase();
                    if (this.LetrasU.indexOf(tecla) == -1) {
                        evt.stopEvent();
                        return false;
                    }
                    break;
                case 'a':
                    tecla = tecla.toLowerCase();
                    if (this.LetrasL.indexOf(tecla) == -1) {
                        evt.stopEvent();
                        return false;
                    }
                    break;
                case 'Z':
                    if (this.Letras.indexOf(tecla) == -1) {
                        evt.stopEvent();
                        return false;
                    }
                    break;
                case '*':
                    break;
                default:
                    evt.stopEvent();
                    return false;
            }

            value = value.slice(0, start) + tecla + value.slice(end);
            field.setValue(value);

            objDom.selectionStart = objDom.selectionEnd = start + 1;
            evt.stopEvent();
            return false;
        }
    }
});